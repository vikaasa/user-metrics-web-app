from flask import render_template, request, url_for, flash, redirect
from app import app
import json
from collections import defaultdict
posted_metrics = defaultdict(list)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='User Metrics',
                           posts=posted_metrics
)

@app.route('/create')
def create():
  return render_template('create.html')

@app.route('/result', methods=['GET','POST'])
def result():
    if request.method == 'POST':
        # do stuff when the form is submitted
        res = request.form.copy()
        metric_name = res['ColName']
        res.pop('ColName')
        res.pop('btnSub')
        posted_metrics[metric_name].extend([float(i) for i in res.values()])
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))
    # show the form, it wasn't submitted
    return redirect(url_for('index'))

@app.route('/stats', methods=['GET','POST'])
def stats():
  def median(lst):
    lst = sorted(lst)
    if len(lst) < 1:
            return None
    if len(lst) %2 == 1:
            return lst[((len(lst)+1)/2)-1]
    else:
            return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0
  if request.method == 'POST':
      # do stuff when the form is submitted
      res = request.form.copy()
      res.pop('btnGetStats')
      metric_values = posted_metrics[list(res)[0]]
      mean_value = sum(metric_values)/len(metric_values)
      min_value = min(metric_values)
      max_value = max(metric_values)
      median_value = median(metric_values)

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