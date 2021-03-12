"""Vultr API helper functions."""
import json
import logging
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request
import sys

vultr_api_key = os.environ.get('VULTR_API_KEY')


def raise_if_next_link(response):
  # They don't specify how pagination works in their API docs.
  if response['meta']['links']['next']:
    raise ValueError('Unexpected "next" link.')

def get_backups():
  """GET /backups"""
  response = vultr_api_json_request('/backups')
  raise_if_next_link(response)
  return response['backups']


def get_instances():
  """GET /instances."""
  response = vultr_api_json_request('/instances')
  raise_if_next_link(response)
  return response['instances']

def get_instance(id):
  """GET /instances/{id}"""
  response = vultr_api_json_request(f'/instances/{id}')
  return response['instance']


def create_instance(region, plan, snapshot_id, firewall_group_id, label):
  """POST /instances."""
  data = {
    'region': region,
    'plan': plan,
    'label': label,
    'snapshot_id': snapshot_id,
    'firewall_group_id': firewall_group_id,
  }
  response = vultr_api_json_request('/instances', verb='POST', data=data)
  logging.debug(json.dumps(response))
  return response['instance']

def delete_instance(id):
  """DELETE /instances/{id}"""
  vultr_api_json_request(f'/instances/{id}', verb='DELETE')


def vultr_api_json_request(url_segment, verb='GET', data=None):
  if vultr_api_key is None:
    raise ValueError('VULTR_API_KEY not found.')

  request = urllib.request.Request(
      f'https://api.vultr.com/v2{url_segment}', method=verb)
  request.add_header('Authorization', 'Bearer ' + vultr_api_key)

  try:
    if verb == 'POST':
      request.add_header('Content-Type', 'application/json; charset=utf-8')
      data_string = json.dumps(data)
      data_bytes = data_string.encode('utf-8')   # needs to be bytes
      request.add_header('Content-Length', len(data_bytes))
      content = urllib.request.urlopen(request, data_bytes).read()
    else:
      content = urllib.request.urlopen(request).read()
    
    logging.debug(f'API response: {content}')
    return json.loads(content) if content else None

  except urllib.error.HTTPError as e:
    response = e.read().decode()
    logging.error(f'HTTP Error {e.code} ({e.reason}):\n\n{response}')
    sys.exit(1)

