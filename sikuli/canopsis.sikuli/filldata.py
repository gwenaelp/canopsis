#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import time, json, pprint, datetime, sys
from kombu import Connection
from kombu.pools import producers
from random import randint, random, choice

pp = pprint.PrettyPrinter(indent=4)

# about 1 months
duration = 3600*24*365
timestamp = int(time.time())
frequency = 3600*24
statuses = ['ok','warning','critical','unknown']


if '--help' in sys.argv or '-h' in sys.argv or 'help' in sys.argv:
     print """
Canopsis data feed helper
     launch with no params to start real time data send daemon (normal mode)
     launch with --debug for debug verbose execution
     launch with init parameter for past event reconstruction (do it once)
"""
     sys.exit(0)    

DEBUG = 0
if '--debug' in sys.argv or '-d' in sys.argv:
     DEBUG = 1

# Configurations
host = "127.0.0.1"
port = 5672
user = "guest"
password = "guest"
vhost = "canopsis"
exchange = "canopsis.events"

event = {
     "connector":        "sikulidata",
     "connector_name":   "sikulidata2amqp",
     "event_type":       "check",
     "source_type":      "resource",
     "component":        "sikuli",
     "resource":         "scenario",
     "state":            0,
     "state_type":       1,
     "output":           "Send data to AMQP for sikuli scenario",
     "display_name":     "Sikuli",
    'perf_data_array': [
     {
          "metric" : "hosts_up",
          "value"  : 150,
          "type"   : "GAUGE",
     },
     {
          "metric" : "hosts_down",
          "value"  : 0,
          "type"   : "GAUGE",
     },
],
}

events = {event_name: event.copy() for event_name in ['hosts', 'services', 'statuses_emulator', 'infra_emulator','message_generator', 'progress_bar_generator']}

#Service initialization
events['services']['resource'] = 'services'
events['services']['perf_data_array'] =  [
          {
               "metric" : "services_up",
               "value"  : 150,
               "type"   : "GAUGE",
          },
          {
               "metric" : "services_down",
               "value"  : 0,
               "type"   : "GAUGE",
          }
     ]
events['statuses_emulator']['component'] = 'status_emulator'
events['statuses_emulator']['perf_data_array'] =  [
          {
               "metric" : "status",
               "value"  : 0,
               "type"   : "GAUGE",
          },
     ]
events['infra_emulator']['resource'] = 'ping_infrastructure'
events['infra_emulator']['perf_data_array'] = []

events['message_generator']['component'] = 'messages_fonctionels'

events['message_generator']['display_name'] = 'messages de service'   
events['progress_bar_generator']['resource'] = 'disk'
events['progress_bar_generator']['perf_data_array'] =  [
          {
               "metric" : 'used',
               "value"  : 0,
               "type"   : "GAUGE",
               'min'      : 0,
               'max'      : 100,
               'warn'     : 75,
               'crit'     : 90
          },
     ]


def publish(event):
     routing_key = "%s.%s.%s.%s.%s" % (event['connector'], event['connector_name'], event['event_type'], event['source_type'], event['component'])
     if DEBUG:
          print 'publishing',routing_key

     producer.publish(
                    event,
                    serializer='json',
                    exchange=exchange,
                    routing_key=routing_key)


""" Business layer """


# Generates a curve witch sometimes fall a bit from maximum value to simulate a service / host loss on network
def activity_ping(activity_type):
     if DEBUG:
          print 'Host ping'

     event = events[activity_type]

     # activity downs
     if random() > 0.99:
          fault = randint(1,3)
          event['perf_data_array'][0]['value'] -= fault
          event['perf_data_array'][1]['value'] += fault
     # activity ups
     if event['perf_data_array'][0]['value'] < 150 and random() > 0.95:
          event['perf_data_array'][0]['value'] += 1    
          event['perf_data_array'][1]['value'] -= 1    
                         
     return event


# Genetates statuses events which only aims to be displayed as pie chart proportions
def statuses_emulator():
     if DEBUG:print 'statuses generator'

     event = events['statuses_emulator']
     left = 40
     
     
     for status in range(4):
     
          if status != 3:
               send_event = randint(0,left)
          else:
               send_event = left
     
          left -= send_event
          event['perf_data_array'][0]['metric'] = 'generated_status_' + statuses[status]
          event['perf_data_array'][0]['value']  = send_event
          publish(event)

          if DEBUG:
               print 'left', left, 'status', statuses[status]


# Genetates statuses events which only aims to be displayed as pie chart proportions
def infra_emulator():
     if DEBUG:
          print 'infra generator'

     event = events['infra_emulator']

     infras = ['mails','dns', 'dhcp','web_server','databases', 'erp', 'hosts_down', 'active_directory', 'pof', 'pot']
     
     for infra in infras:

          #each infr gets 10 servers
          for evt in xrange(10): 
               event['component'] = "%s_%s" % (infra, evt)
               if random() > 0.98:
                    event['state'] = randint(1,3)
               else:
                    event['state'] = 0
                    
               publish(event)

               if DEBUG:
                    print 'generated %s number %s infrastructure with %s status' % (infra, evt, statuses[int(event['state'])])


def message_generator(ts):
     services_messages = [
          "Jour férié , le 11 Novembre interruption des activités",
          "Coupure générale du système électrique durant 30 minutes à 15H le 12/09/2013",
          "Panne réseau sur le secteur 1 toujours en cours",
          "Equipe technique en intervention pour le client 1337",
          "Support technique en grève ce jour",
          "Fête nationale en chine demain, baisee d'activité à prévoir",
          "Améliorations des systèmes informatique prévue dans une semaine"     
     ]

     if DEBUG:
          print 'message_generator'

     event = events['message_generator']
     event['output'] = choice(services_messages)
     events['message_generator']['connector_name'] = 'messages_de_service_' + str(int(ts))     
     publish(event)
     
# Genetates statuses events which only aims to be displayed as pie chart proportions
def progress_bar_generator():
     if DEBUG:
          print 'statuses generator'

     event = events['progress_bar_generator']
     
     for component in ['file_share', 'mailer', 'media_host']:
          event['component'] = component     
          
          events['progress_bar_generator']['perf_data_array'][0]['value'] += randint(1,10)
          if events['progress_bar_generator']['perf_data_array'][0]['value'] > 100:
               events['progress_bar_generator']['perf_data_array'][0]['value'] = 0
     
          publish(event)

          if DEBUG:
               print 'progress_bar',event['component'],events['progress_bar_generator']['perf_data_array'][0]['value']


     
""" Global business function """        
def send_events(ts):
     # Update all events to the right timestamp
     for key in events:
          events[key]['timestamp'] = ts 

     publish(activity_ping('hosts'))    
     publish(activity_ping('services'))
     
     if ts > timestamp:
          if DEBUG:
               print 'Real time function will process'

          statuses_emulator()
          infra_emulator()
          message_generator(ts)         
          progress_bar_generator()      
     

""" End business layer """

""" Program entry points
first, events from past are generated depending on window time defined
then, events are generated in real time
"""


# back to the future (build history)
with Connection(hostname=host, userid=user, virtual_host=vhost) as conn:
     with producers[conn].acquire(block=True) as producer:
          if 'init' in sys.argv:
               for t in xrange(0, duration, frequency):
                    print 'paste generator', int(t/frequency), '/', int(duration/frequency)
                    ts = timestamp - duration + t
                    if DEBUG:
                         print 'timestamp', ts
                    send_events(ts)
               
               print 'rewriting paste... Done.'

          # Starts sending event in real time
          while True:
               send_events(time.time())
               print 'Realtime data simulation. Events sent @ ', str(datetime.datetime.now())
               time.sleep(60)