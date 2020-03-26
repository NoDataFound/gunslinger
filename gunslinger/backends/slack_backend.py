import slack
import time

class Slack_MQ():

    def __init__(self, slack_token, queue_channel=None):
        if queue_channel is None:
            queue_channel = 'mq'
        self.client = slack.WebClient(token=slack_token)
        print(f'Channel is {queue_channel}')
        self.channel = self.get_channel(queue_channel)


    def get_channel(self, channel):
        """Gets ID of Slack channel.

        Arguments:
            channel (str): channel to get ID of

        Returns:
            str: Channel ID
        """
        print(f'Getting channel {channel}')
        channels = self.client.conversations_list()
        for slack_channel in channels['channels']:
            if slack_channel['name'] == channel:
                return slack_channel['id']
        raise Exception('Channel does not exist')


    def post_message(self, text, **kwargs):
        channel = kwargs.get('channel', self.channel)
        reaction = kwargs.get('reaction', '')
        message_response = self.client.chat_postMessage(channel=channel,
                                                        text=text)
        if reaction:
            self.react_message(message_response['ts'],
                               reaction,
                               channel)
        return message_response


    def react_message(self, ts, reaction, channel=''):
        if channel == '':
            channel = self.channel
        reaction_response = self.client.reactions_add(channel=channel,
                                                      name=reaction,
                                                      timestamp=ts)
        return reaction_response


    def get_next_message(self, **kwargs):
        limit = kwargs.get('limit', 999)
        oldest = kwargs.get('oldest', 0)
        latest = kwargs.get('latest', '')
        cursor = kwargs.get('cursor', '')
        try:
            r = self.client.conversations_history(channel=self.channel,
                                                  limit=999,
                                                  oldest=str(oldest),
                                                  latest=str(latest),
                                                  inclusive=1,
                                                  cursor=cursor)
            data = r.data
            messages = data['messages']
            i = 0
            for i in range(len(messages)-1):
                m = messages[i]
                if 'reactions' in messages[i+1] and 'New batch' in m['text'] \
                   and not 'reactions' in m.keys():
                    ts = m['ts']
                    self.client.reactions_add(channel=self.channel,
                                              name='+1',
                                              timestamp=ts)
                    oldest = ts
                    dat = m['text'].strip().split('\n')[1:]
                    return dat, oldest
                elif 'reactions' in m.keys():
                    return [], 0
            if 'reactions' in messages[i] and 'New batch' in \
               messages[i]['text']:
                ts=messages[i]['ts']
                self.client.reactions_add(channel=self.channel,
                                          name='+1',
                                          timestamp=ts)
                oldest = ts
                dat = m['text'].strip().split('\n')[1:]
                return dat, oldest
            else:
                if 'response_metadata' in data.keys() and \
                   'next_cursor' in data['response_metadata'].keys():
                    print('Getting next cursor')
                    cursor=data['response_metadata']['next_cursor']
                    return self.get_next_message(oldest=oldest,
                                                 latest=latest,
                                                 cursor=cursor)
                return [], latest
        except Exception as e:
            print(e)
            if 'response' in dir(e):
                r = e.response
                print(r)
                time.sleep(60)
                if r['error'] == 'ratelimited':
                    return self.get_next_message(oldest=oldest,
                                                 latest=latest,
                                                 cursor=cursor)
                else:
                    return [],0
            else:
                return [],oldest

