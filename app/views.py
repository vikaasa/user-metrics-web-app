from flask import render_template, request, url_for, flash, redirect, Flask, jsonify, abort
from app import app
import json
from collections import defaultdict
from flask import make_response
from heapq import *

posted_metrics = {}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='User Metrics',
                           posts=posted_metrics
)
#curl -i -H "Content-Type: application/json" -X POST -d '{"title":"sample"}' http://localhost:5000/create
@app.route('/create', methods=['GET','POST'])
def create():
  if request.method == 'POST':
    # if 'title' not present in POST request, return bad request
    if not request.json or not 'title' in request.json:
      abort(400)
    if request.json['title'] not in posted_metrics:
      metric = {
        'values': [],
        'min': None,
        'max': None,
        'mean': None,
        'median': None,
        'sum':0,
        'small_heap': [],
        'large_heap': []}
      posted_metrics[request.json['title']] = metric
      return jsonify({'message':str(request.json['title'])+' created'}), 201
    else:
      abort(409)
  else:
    return render_template('create.html')

#curl -i -H "Content-Type: application/json" -X POST -d '{"title":"sample","value":"100"}' http://localhost:5000/post
@app.route('/post', methods=['POST'])
def post():
  # if 'title' not present in POST request, return bad request
  if not request.json or not 'title' in request.json or not 'value' in request.json:
    abort(400)  
    #return jsonify({'message': 'value added to ' + str(request.json)}), 201
  if request.json['title'] not in posted_metrics:
    abort(404)
  else:
    try:
      value = float(request.json['value'])
    except:
      abort(422)
    posted_metrics[request.json['title']]['values'].append(value)
    posted_metrics[request.json['title']]['min'] = min(posted_metrics[request.json['title']]['min'],value) if posted_metrics[request.json['title']]['min'] is not None else value
    posted_metrics[request.json['title']]['max'] = max(posted_metrics[request.json['title']]['max'],value) if posted_metrics[request.json['title']]['max'] is not None else value
    posted_metrics[request.json['title']]['sum'] = posted_metrics[request.json['title']]['sum']+value if posted_metrics[request.json['title']]['sum'] is not None else value
    posted_metrics[request.json['title']]['mean'] = float(posted_metrics[request.json['title']]['sum']/len(posted_metrics[request.json['title']]['values']))
    posted_metrics[request.json['title']]['median'] = calculate_median(posted_metrics[request.json['title']]['small_heap'], posted_metrics[request.json['title']]['large_heap'], value)
    return jsonify({'message': 'value added to ' + str(request.json['title'])}), 201

# calculate median by maintaining and balancing the sizes of two heaps. Adding a value takes O(log n) time, and median is re-computed in O(1) time after every add.
def calculate_median(small_heap, large_heap, val):
  heappush(small_heap, -heappushpop(large_heap, val))
  if len(large_heap) < len(small_heap):
      heappush(large_heap, -heappop(small_heap))
  if len(large_heap) > len(small_heap):
      return float(large_heap[0])
  return (large_heap[0] - small_heap[0]) / 2.0

#curl -i http://localhost:5000/get/sample
@app.route('/get/<metric_name>', methods=['GET'])
def get_metric(metric_name):
  if metric_name not in posted_metrics:
    abort(404)
  else:
    metric = posted_metrics[metric_name]
        
    return jsonify({
                    'mean': posted_metrics[metric_name]['mean'],
                    'median': posted_metrics[metric_name]['median'],
                    'min': posted_metrics[metric_name]['min'],
                    'max': posted_metrics[metric_name]['max']})

#curl -i http://localhost:5000/getlist
@app.route('/getlist', methods=['GET'])
def get_all_metrics(): 
    return jsonify({'metrics': sorted(posted_metrics.keys())})

#curl -i http://localhost:5000/getvalues/sample
@app.route('/getvalues/<metric_name>', methods=['GET'])
def get_values(metric_name):
  if metric_name not in posted_metrics:
    abort(404)
  else:
    metric = posted_metrics[metric_name]
    return jsonify({'values': posted_metrics[metric_name]['values']})

@app.route('/result', methods=['GET','POST'])
def result():
  if request.method == 'POST':
      # do stuff when the form is submitted
      res = request.form.copy()
      metric_name = res['ColName']
      res.pop('ColName')
      res.pop('btnSub')
      new_values = [float(i) for i in res.values()]
      if metric_name not in posted_metrics:
        metric = {
          'values': [],
          'min': None,
          'max': None,
          'mean': None,
          'median': 0.0,
          'sum':0.0,
          'small_heap': [],
          'large_heap': []}
        posted_metrics[metric_name] = metric
      posted_metrics[metric_name]['sum'] = posted_metrics[metric_name]['sum'] + sum(new_values)
      posted_metrics[metric_name]['mean'] = posted_metrics[metric_name]['sum']/(len(posted_metrics[metric_name]['values'])+len(new_values))
      for i in new_values:
        posted_metrics[metric_name]['median'] = calculate_median(posted_metrics[metric_name]['small_heap'], posted_metrics[metric_name]['large_heap'], i)
      posted_metrics[metric_name]['min'] = min(posted_metrics[metric_name]['min'], min(new_values)) if posted_metrics[metric_name]['min'] is not None else min(new_values)
      posted_metrics[metric_name]['max'] = max(posted_metrics[metric_name]['max'], max(new_values)) if posted_metrics[metric_name]['max'] is not None else max(new_values)
      posted_metrics[metric_name]['values'].extend(new_values)
      # redirect to end the POST handling
      # the redirect can be to the same route or somewhere else
      return redirect(url_for('index'))
  # show the form, it wasn't submitted
  return redirect(url_for('index'))

@app.route('/stats', methods=['GET','POST'])
def stats():
  if request.method == 'POST':
      # do stuff when the form is submitted
      res = request.form.copy()
      res.pop('btnGetStats')
      metric_name = list(res)[0]
      metric_values = posted_metrics[metric_name]['values']
      mean_value = posted_metrics[metric_name]['mean']
      min_value = posted_metrics[metric_name]['min']
      max_value = posted_metrics[metric_name]['max']
      median_value = posted_metrics[metric_name]['median']

      # redirect to end the POST handling
      # the redirect can be to the same route or somewhere else
      return render_template('statistics.html',
                           m_values=metric_values,
                           metric_name=list(res)[0],
                           metric_mean=mean_value,
                           metric_min = min_value,
                           metric_max = max_value,
                           metric_median = median_value,
                           table_len = len(metric_values))
  # show the form, it wasn't submitted
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify({'error': 'Metric already exists, please choose a different name'}), 409)

@app.errorhandler(422)
def invalid_input(error):
    return make_response(jsonify({'error': 'Invalid value, please enter a valid decimal number'}), 422)