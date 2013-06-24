"""
>>> mp = mixpanel.Mixpanel('TOKEN')
>>> mp.track('Button Clicked')
>>> mp.track('Button Clicked', {'Account Type': 'Premium'})
>>> mp.set('DISTINCT_ID', {'Account Type': 'Premium'})
>>> mp.unset('DISTINCT_ID', ['Hello'])
>>> mp.add('DISTINCT_ID', {'Account Type': 'Premium'})
>>> mp.append('DISTINCT_ID', {')
>>> mp.union('DISTINCT_ID', {'Favorite Teams': ['Leafs', 'Jays']})
>>> mp.delete('DISTINCT_ID')

mp = mixpanel.Mixpanel('TOKEN')
mp.track('Button Clicked', {
})

mp.set('123', {'Account Type': 'Free'})
mp.unset('123', ['Account Type'])
mp.add('123', {'Comments Made': 1})
mp.union('123', {'': ['Free', '']})
mp.delete('123')

mp = mixpanel.Mixpanel('TOKEN')
mp.track_batch([
    {
        'event': 'Button Clicked',
        'properties': {
            'distinct_id': 'userid1',
            'Account Type': 'Premium',
        }
    },
    {
        'event': 'Sign Up',
        'properties': {
            'distinct_id': 'userid2',
            'Account Type': 'Free',
        }
    },
])

mp = mixpanel.Mixpanel('TOKEN')
mp.engage_batch([
    {
        '$distinct_id': 'userid1',
        '$set': {
            'Account Type': 'Premium',
        }
    },
    {
        '$distinct_id': 'userid2',
        '$set': {
            'Account Type': 'Free',
        }
    },
    {
        '$distinct_id': 'userid3',
        '$add': {
            'Videos Watched': 1,
        }
    },
])

"""

import base64
import json
import urllib
import urllib2

class Mixpanel(object):

    def __init__(self, token, base_url='https://api.mixpanel.com', batch=False):
        self._token = token
        self._base_url = base_url

    def _write(self, endpoint, data, **params):
        if len(data) > 50:
            raise ValueError('batch exceeds 50 item max')
        params['data'] = base64.b64encode(json.dumps(data, separators=(',', ':')))
        params['verbose'] = 1
        response = json.load(urllib2.urlopen(self._base_url + endpoint, urllib.urlencode(params)))
        if response['status'] == 0:
            raise RuntimeError(response['error'])

    def alias(self, alias, distinct_id):
        self.track('$create_alias', {'alias': alias, 'distinct_id': distinct_id})

    def track(self, event_name, properties={}, geolocate_ip=False):
        event = {'event': event_name, 'properties': properties}
        self.track_batch([event], geolocate_ip=geolocate_ip)

    def track_batch(self, events, geolocate_ip=False):
        for event in events:
            event['properties']['token'] = self._token
            self._validate_event(event)
        self._write('/track', events, ip=1 if geolocate_ip else 0)

    def engage(self, op, distinct_id, properties, geolocate_ip=False, time=None, update_last_seen=False):
        record = {
            '$token': token,
            '$distinct_id': distinct_id,
             op: properties,
        }
        if time is not None:
            record['$time'] = time
        self.engage_batch([record], geolocate_ip=geolocate_ip, update_last_seen=update_last_seen)

    def engage_batch(self, records, geolocate_ip=False, update_last_seen=False):
        for record in records:
            record['$token'] = self._token
            if '$ignore_time' not in record and not update_last_seen:
                record['$ignore_time'] = True
            self._validate_record(record)
        self._write('/engage', records, ip=1 if geolocate_ip else 0)

    def set(self, distinct_id, properties, geolocate_ip=False, time=None, update_last_seen=False):
        self.engage('$set', distinct_id, properties, geolocate_ip=geolocate_ip, time=time, update_last_seen=update_last_seen)

    def set_once(self, distinct_id, properties, geolocate_ip=False, time=None, update_last_seen=False):
        self.engage('$set_once', distinct_id, properties, geolocate_ip=geolocate_ip, time=time, update_last_seen=update_last_seen)

    def unset(self, distinct_id, properties, geolocate_ip=False, time=None, update_last_seen=False):
        self.engage('$unset', distinct_id, properties, geolocate_ip=geolocate_ip, time=time, update_last_seen=update_last_seen)

    def add(self, distinct_id, properties, geolocate_ip=False, time=None, update_last_seen=False):
        self.engage('$add', distinct_id, properties, geolocate_ip=geolocate_ip, time=time, update_last_seen=update_last_seen)

    def append(self, distinct_id, properties, geolocate_ip=False, time=None, update_last_seen=False):
        self.engage('$append', distinct_id, properties, geolocate_ip=geolocate_ip, time=time, update_last_seen=update_last_seen)

    def union(self, distinct_id, properties, geolocate_ip=False, time=None, update_last_seen=False):
        self.engage('$union', distinct_id, properties, geolocate_ip=geolocate_ip, time=time, update_last_seen=update_last_seen)

    def delete(self, distinct_id):
        self.engage('$delete', distinct_id, {})
