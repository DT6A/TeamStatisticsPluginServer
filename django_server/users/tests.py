import json
import random

from django.test import TestCase
from django.test import Client

from .models import *
from .views import aggregate_notes


class DataSendingTest(TestCase):
    def test_get(self):
        c = Client()
        response = c.get('/post/')
        self.assertEqual(response.status_code, 404)

    def test_incorrect_data_send(self):
        c = Client()

        self.assertEqual(c.post('/post/', json.dumps({}), content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/post/', json.dumps({'token': 't',
                                                      'time_from': '2021-05-23 14:24:20+00:00',
                                                      'time_to': '2021-05-23 14:24:20+00:00'}),
                                content_type="application/json").status_code, 404)
        self.assertEqual(0, len(UserStat.objects.all()))
        u = User.objects.create_user(username='testuser', password='12345')
        self.assertEqual(c.post('/post/', json.dumps({'time_from': '2021-05-23 14:24:20+00:00',
                                                      'time_to': '2021-05-23 14:24:20+00:00'}),
                                content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/post/', json.dumps({'token': u.useruniquetoken.token,
                                                      'time_to': '2021-05-23 14:24:20+00:00'}),
                                content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/post/', json.dumps({'token': u.useruniquetoken.token,
                                                      'time_from': '2021-05-23 14:24:20+00:00'}),
                                content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/post/', json.dumps({'token': 'random',
                                                      'time_from': '2021-05-23 14:24:20+00:00',
                                                      'time_to': '2021-05-23 14:24:20+00:00'}),
                                content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/post/', json.dumps({'token': u.useruniquetoken.token,
                                                      'time_from': '2021-05-23 14:24:20+00:00',
                                                      'time_to': '2021-05-23 14:24:20+00:00'}),
                                content_type="application/json").status_code, 200)
        self.assertEqual(1, len(UserStat.objects.all()))

    def test_correct_data_send(self):
        n_users = 5
        max_sends = 5
        users = []
        notes_n = []
        c = Client()

        for i in range(n_users):
            users.append(User.objects.create_user(username='testuser' + str(i), password='12345'))

        self.assertEqual(0, len(UserStat.objects.all()))
        for user in users:
            notes_n.append(random.randint(1, max_sends))
            for i in range(notes_n[-1]):
                self.assertEqual(c.post('/post/', json.dumps({'token': user.useruniquetoken.token,
                                                              'time_from': '2021-05-23 14:24:20+00:00',
                                                              'time_to': '2021-05-23 14:24:20+00:00'}),
                                        content_type="application/json").status_code, 200)

        self.assertEqual(sum(notes_n), len(UserStat.objects.all()))

        for user, n in zip(users, notes_n):
            self.assertEqual(n, len(UserStat.objects.filter(user=user)))

    def test_correctly_puts_and_aggregates_data(self):
        n_sends = 10
        user_1_metrics = {'metric_1': 0, 'metric_2': 0}
        user_2_metrics = {'metric_1': 0, 'metric_2': 0}
        c = Client()

        user_1 = User.objects.create_user(username='testuser1', password='12345')
        user_2 = User.objects.create_user(username='testuser2', password='12345')

        self.assertEqual(0, len(UserStat.objects.all()))

        for i in range(n_sends):
            if random.randint(0, 1) == 0:
                u = user_1
                d = user_1_metrics
            else:
                u = user_2
                d = user_2_metrics
            metric_key = f'metric_{random.randint(1, 2)}'
            metric_val = random.randint(1, 1000)
            self.assertEqual(c.post('/post/', json.dumps({'token': u.useruniquetoken.token,
                                                          'time_from': '2021-05-23 14:24:20+00:00',
                                                          'time_to': '2021-05-23 14:24:20+00:00',
                                                          metric_key: metric_val
                                                          }),
                                    content_type="application/json").status_code, 200)
            d[metric_key] += metric_val
            self.assertEqual(d[metric_key], aggregate_metric_all_time(u, metric_key))

        self.assertEqual(n_sends, len(UserStat.objects.all()))

    def test_aggregating(self):
        user = User.objects.create_user(username='testuser1', password='12345')
        c = Client()

        def make_query_with_date(f, t):
            self.assertEqual(c.post('/post/', json.dumps({'token': user.useruniquetoken.token,
                                                          'time_from': f,
                                                          'time_to': t,
                                                          'metric': 1
                                                          }),
                                    content_type="application/json").status_code, 200)

        # > year
        make_query_with_date((datetime.today() - timedelta(days=3000)).isoformat(),
                             (datetime.today() - timedelta(days=3000)).isoformat())
        make_query_with_date((datetime.today() - timedelta(days=1000)).isoformat(),
                             (datetime.today() - timedelta(days=1000)).isoformat())
        make_query_with_date((datetime.today() - timedelta(days=700)).isoformat(),
                             (datetime.today() - timedelta(days=700)).isoformat())
        make_query_with_date((datetime.today() - timedelta(days=400)).isoformat(),
                             (datetime.today() - timedelta(days=400)).isoformat())
        # > month
        make_query_with_date((datetime.today() - timedelta(days=40)).isoformat(),
                             (datetime.today() - timedelta(days=40)).isoformat())
        make_query_with_date((datetime.today() - timedelta(days=31)).isoformat(),
                             (datetime.today() - timedelta(days=31)).isoformat())
        make_query_with_date((datetime.today() - timedelta(days=70)).isoformat(),
                             (datetime.today() - timedelta(days=70)).isoformat())
        # > week
        make_query_with_date((datetime.today() - timedelta(days=29)).isoformat(),
                             (datetime.today() - timedelta(days=29)).isoformat())
        make_query_with_date((datetime.today() - timedelta(days=8)).isoformat(),
                             (datetime.today() - timedelta(days=8)).isoformat())
        # > day
        make_query_with_date((datetime.today() - timedelta(days=6)).isoformat(),
                             (datetime.today() - timedelta(days=6)).isoformat())
        make_query_with_date((datetime.today() - timedelta(days=2)).isoformat(),
                             (datetime.today() - timedelta(days=2)).isoformat())
        # < day
        make_query_with_date(datetime.today().isoformat(), datetime.today().isoformat())
        make_query_with_date(datetime.today().isoformat(), datetime.today().isoformat())
        make_query_with_date(datetime.today().isoformat(), datetime.today().isoformat())
        make_query_with_date(datetime.today().isoformat(), datetime.today().isoformat())
        make_query_with_date(datetime.today().isoformat(), datetime.today().isoformat())

        aggregate_notes(user, 10)
        self.assertEqual(len(UserStat.objects.all()), 9)
        self.assertEqual(aggregate_metric_all_time(user, 'metric'), 16)

        def aggregate_dt(delta):
            s = extract_metric(UserStat.objects.filter(user=user, time_from__gte=datetime.now() - delta), 'metric')
            return s if s else 0

        self.assertEqual(aggregate_dt(timedelta(days=1)), 5)
        self.assertEqual(aggregate_dt(timedelta(days=7)), 7)
        self.assertEqual(aggregate_dt(timedelta(days=30)), 9)
        self.assertEqual(aggregate_dt(timedelta(days=365)), 12)


class PluginLoginTest(TestCase):
    def test_get(self):
        c = Client()
        response = c.get('/plugin_login/')
        self.assertEqual(response.status_code, 404)

    def test_login(self):
        c = Client()
        username = 'testuser'
        password = '12345'
        u = User.objects.create_user(username=username, password=password)
        u2 = User.objects.create_user(username=username + '2', password=password + '2')
        self.assertEqual(c.post('/plugin_login/', json.dumps({}), content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/plugin_login/', json.dumps({'username': username,
                                                              }),
                                content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/plugin_login/', json.dumps({'password': password,
                                                              }),
                                content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/plugin_login/', json.dumps({'username': '123',
                                                              'password': password,
                                                              }),
                                content_type="application/json").status_code, 404)
        self.assertEqual(c.post('/plugin_login/', json.dumps({'username': username,
                                                              'password': 'password',
                                                              }),
                                content_type="application/json").status_code, 401)
        self.assertEqual(c.post('/plugin_login/', json.dumps({'username': username,
                                                              'password': password + '2',
                                                              }),
                                content_type="application/json").status_code, 401)
        self.assertEqual(c.post('/plugin_login/', json.dumps({'username': username + '2',
                                                              'password': password,
                                                              }),
                                content_type="application/json").status_code, 401)
        response = c.post('/plugin_login/', json.dumps({'username': username + '2',
                                                              'password': password + '2',
                                                              }),
                                content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], u2.useruniquetoken.token)
        response = c.post('/plugin_login/', json.dumps({'username': username,
                                                        'password': password,
                                                        }),
                          content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], u.useruniquetoken.token)


class MetricsReceiving(TestCase):
    def test_empty_metrics(self):
        c = Client()

        response = c.get('/plugin_get_all_metrics/')
        j_response = response.json()
        self.assertEquals([], j_response[CHAR_COUNTER])
        self.assertEquals([], j_response[WORD_COUNTER])

    def test_some_metrics_exist(self):
        CharCountingMetric(name='1', char='1').save()
        CharCountingMetric(name='2', char='2').save()
        SubstringCountingMetric(name='str1', substring='str1').save()
        SubstringCountingMetric(name='str2', substring='str2').save()

        c = Client()

        response = c.get('/plugin_get_all_metrics/')
        j_response = response.json()

        self.assertEquals(['1', '2'], j_response[CHAR_COUNTER])
        self.assertEquals(['str1', 'str2'], j_response[WORD_COUNTER])
