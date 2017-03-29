#!flask/bin/python
import os
import unittest
from app import app
#from app.views import posted_metrics, create
import app.views as views

from unittest import TestCase
from webtest import TestApp
import json

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_createMetric(self):
        # testing create a metric
        views.posted_metrics = {} #resetting state
        #self.app = app.test_client()
        #print self.app.get('/')
        response = self.app.post('/create', 
                       data=json.dumps({"title":"sample"}),
                       content_type='application/json')
        expected = { "sample" : {
                        'values': [],
                        'min': None,
                        'max': None,
                        'mean': None,
                        'median': None,
                        'sum':0,
                        'small_heap': [],
                        'large_heap': []}
                        }
        self.assertEqual(views.posted_metrics, expected)

    def test_detectConflict(self):
        # detect if metric already exists
        
        # initializing posted_metrics with existing name
        views.posted_metrics = {"existing_name" : {
                                    'values': [],
                                    'min': None,
                                    'max': None,
                                    'mean': None,
                                    'median': None,
                                    'sum':0,
                                    'small_heap': [],
                                    'large_heap': []}} 

        response = self.app.post('/create', 
                       data=json.dumps({"title":"existing_name"}),
                       content_type='application/json')
        self.assertEqual(response.status_code, 409)

    def test_badRequest(self):
        # test if request is in wrong format
        response = self.app.post('/create', 
                       data=json.dumps({"wrong_header":"sample"}),
                       content_type='application/json')
        self.assertEqual(response.status_code, 400)    

    def test_postMetrics(self):
        # test to check posting a metric
        
        # initializing posted_metrics
        views.posted_metrics = {"sample" : {
                                    'values': [],
                                    'min': None,
                                    'max': None,
                                    'mean': None,
                                    'median': None,
                                    'sum':0,
                                    'small_heap': [],
                                    'large_heap': []}} 

        response = self.app.post('/post', 
                       data=json.dumps({"title":"sample", "value":"90"}),
                       content_type='application/json')
        #print response
        #print views.posted_metrics
        expected = {"sample" : {
                        'values': [90],
                        'min': 90,
                        'max': 90,
                        'mean': 90,
                        'median': 90,
                        'sum':90,
                        'small_heap': [],
                        'large_heap': [90]}}

        self.assertEqual(views.posted_metrics, expected)

        response = self.app.post('/post', 
               data=json.dumps({"title":"sample", "value":"74"}),
               content_type='application/json')
        response = self.app.post('/post', 
               data=json.dumps({"title":"sample", "value":"95.5"}),
               content_type='application/json')
        expected = {"sample" : {
                        'values': [90.0,74.0,95.5],
                        'min': 74.0,
                        'max': 95.5,
                        'mean': 86.5,
                        'median': 90.0,
                        'sum':259.5,
                        'small_heap': [-74.0],
                        'large_heap': [90.0,95.5]}}
        
        self.assertEqual(views.posted_metrics, expected)

        response = self.app.post('/post', 
               data=json.dumps({"title":"sample", "value":"97.5"}),
               content_type='application/json')

        expected = {"sample" : {
                        'values': [90.0,74.0,95.5,97.5],
                        'min': 74.0,
                        'max': 97.5,
                        'mean': 89.25,
                        'median': 92.75,
                        'sum':357.0,
                        'small_heap': [-90.0,-74.0],
                        'large_heap': [95.5,97.5]}}
        
        #print views.posted_metrics
        self.assertEqual(views.posted_metrics, expected)

        response = self.app.post('/post', 
               data=json.dumps({"title":"sample", "value":"-100.0"}),
               content_type='application/json')

        expected = {"sample" : {
                        'values': [90.0,74.0,95.5,97.5,-100.0],
                        'min': -100.0,
                        'max': 97.5,
                        'mean': 51.4,
                        'median': 90.0,
                        'sum':257.0,
                        'small_heap': [-74.0,100],
                        'large_heap': [90.0,97.5,95.5]}}
        
        #print views.posted_metrics
        self.assertEqual(views.posted_metrics, expected)
    
    def test_checkingInvalidPostRequests(self):
        views.posted_metrics = {"sample" : {
                                    'values': [90.0,74.0,95.5, 97.5],
                                    'min': 74.0,
                                    'max': 97.5,
                                    'mean': 89.25,
                                    'median': 92.75,
                                    'sum':357.0,
                                    'small_heap': [-90.0,-74.0],
                                    'large_heap': [95.5,97.5]}}


        # checking if request has invalid metric name
        response = self.app.post('/post', 
               data=json.dumps({"title":"wrong_name", "value":"97.5"}),
               content_type='application/json')

        self.assertEqual(response.status_code, 404)

        # checking if request is a bad request
        response = self.app.post('/post', 
               data=json.dumps({"wrong_header":"sample", "value":"97.5"}),
               content_type='application/json')

        self.assertEqual(response.status_code, 400)

        # checking if request has invalid value (not a decimal number)
        response = self.app.post('/post', 
               data=json.dumps({"title":"sample", "value":"?"}),
               content_type='application/json')

        self.assertEqual(response.status_code, 422)
        

    def test_getStatistics(self):
        # initializing posted_metrics
        views.posted_metrics = {"sample" : {
                    'values': [90.0,74.0,95.5,97.5],
                    'min': 74.0,
                    'max': 97.5,
                    'mean': 89.25,
                    'median': 92.75,
                    'sum':259.5,
                    'small_heap': [-74.0,-90.0],
                    'large_heap': [95.5,97.5]}}

        # test responses
        response = self.app.get('/get/sample', content_type='application/json')
        #print json.loads(response.data)

        # check if response is OK
        self.assertEqual(response.status_code, 200)
        # check if the GET request has the correct output
        self.assertEqual(json.loads(response.data), {"max": 97.5,
                                                     "mean": 89.25,
                                                     "median": 92.75,
                                                     "min": 74.0})

    def test_getValues(self):
        # initializing posted_metrics
        views.posted_metrics = {"sample" : {
                    'values': [90.0,74.0,95.5,97.5],
                    'min': 74.0,
                    'max': 97.5,
                    'mean': 89.25,
                    'median': 92.75,
                    'sum':259.5,
                    'small_heap': [-74.0,-90.0],
                    'large_heap': [95.5,97.5]}}

        # test responses
        response = self.app.get('/getvalues/sample', content_type='application/json')
        #print json.loads(response.data)

        # check if response is OK
        self.assertEqual(response.status_code, 200)
        # check if the GET request has the correct output
        self.assertEqual(json.loads(response.data), {"values": [90.0,74.0,95.5,97.5]})

    def test_getListOfMetrics(self):
        # initializing posted_metrics
        views.posted_metrics = {"sample_metric_1" : {
                                    'values': [90.0,74.0,95.5,97.5],
                                    'min': 74.0,
                                    'max': 97.5,
                                    'mean': 89.25,
                                    'median': 92.75,
                                    'sum':259.5,
                                    'small_heap': [-74.0,-90.0],
                                    'large_heap': [95.5,97.5]}, 
                                "sample_metric_2" : {
                                    'values': [90],
                                    'min': 90,
                                    'max': 90,
                                    'mean': 90,
                                    'median': 90,
                                    'sum':90,
                                    'small_heap': [],
                                    'large_heap': [90]}}

        # test responses
        response = self.app.get('/getlist', content_type='application/json')
        #print json.loads(response.data)

        # check if response is OK
        self.assertEqual(response.status_code, 200)
        # check if the GET request has the correct output
        self.assertEqual(json.loads(response.data), {"metrics": ["sample_metric_1", "sample_metric_2"]})

    def test_checkingInvalidGetRequests(self):
        # initializing posted_metrics
        views.posted_metrics = {"sample" : {
                    'values': [90.0,74.0,95.5,97.5],
                    'min': 74.0,
                    'max': 97.5,
                    'mean': 89.25,
                    'median': 92.75,
                    'sum':259.5,
                    'small_heap': [-74.0,-90.0],
                    'large_heap': [95.5,97.5]}}

        # test responses
        response = self.app.get('/get/metric_that_does_not_exist', content_type='application/json')
        #print json.loads(response.data)

        # checking response code to verify that metric is not found
        self.assertEqual(response.status_code, 404)

        # test responses
        response = self.app.get('/getvalues/metric_that_does_not_exist', content_type='application/json')
        #print json.loads(response.data)

        # checking response code to verify that metric is not found
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
