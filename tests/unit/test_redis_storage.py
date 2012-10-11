from unittest import TestCase
import json

from mock import patch, MagicMock
import redis


from graphitepager.redis_storage import RedisStorage
from graphitepager.alerts import Alert
from graphitepager.graphite_data_record import GraphiteDataRecord


class TestRedisStorage(TestCase):

    def setUp(self):
        self.r_url = 'Redis URL'
        self.redis = MagicMock(redis)
        self.client = self.redis.from_url()
        self.alert = 'ALERT!'
        self.record = MagicMock(GraphiteDataRecord)()
        self.key = 'ALERT!-incident-key'

        self.rs = RedisStorage(self.redis, self.r_url)

    def should_create_redis_client(self):
        self.redis.from_url.assert_called_with(self.r_url)


class TestRedisStorageGettingIncidentKey(TestRedisStorage):

    def setUp(self):
        super(TestRedisStorageGettingIncidentKey, self).setUp()

    def test_gets_redis_key_from_alert_and_record(self):
        self.client.get.return_value = None
        self.returned = self.rs.get_incident_key_for_alert_key(self.alert)
        self.client.get.assert_called_once_with(self.key)

    def test_no_incident_in_redis(self):
        self.client.get.return_value = None
        self.returned = self.rs.get_incident_key_for_alert_key(self.alert)
        self.assertEqual(self.returned, None)

    def test_incident_in_redis(self):
        self.client.get.return_value = '{"incident": "INCIDENT"}'
        self.returned = self.rs.get_incident_key_for_alert_key(self.alert)
        self.assertEqual(self.returned, 'INCIDENT')


class TestRedisStorageSettingIncidentKey(TestRedisStorage):

    def setUp(self):
        super(TestRedisStorageSettingIncidentKey, self).setUp()
        self.returned = self.rs.set_incident_key_for_alert_key(self.alert, 'INCIDENT')
        self.value = json.dumps({'incident': 'INCIDENT'})

    def test_sets_redis_key_for_alert_and_record(self):
        self.client.set.assert_called_once_with(self.key, self.value)

    def test_sets_key_to_expire(self):
        self.client.expire.assert_called_once_with(self.key, 300)


class TestRedisStorageRemovingIncidentKey(TestRedisStorage):

    def setUp(self):
        super(TestRedisStorageRemovingIncidentKey, self).setUp()
        self.returned = self.rs.remove_incident_for_alert_key(self.alert)

    def test_removes_redis_key_for_alert_and_record(self):
        self.client.delete.assert_called_once_with(self.key)
