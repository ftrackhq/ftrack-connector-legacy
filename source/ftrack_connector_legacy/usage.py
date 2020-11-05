# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import logging

import ftrack_connector_legacy.asynchronous
import ftrack_connector_legacy.session


logger = logging.getLogger('ftrack_connector_legacy:usage')
_log_usage_session = None


def _send_event(event_name, metadata=None):
    '''Send usage event with *event_name* and *metadata*.'''
    global _log_usage_session

    if _log_usage_session is None:
        _log_usage_session = ftrack_connector_legacy.session.get_session()

    try:
        _log_usage_session.call([{
            'action': '_track_usage',
            'data': {
                'type': 'event',
                'name': event_name,
                'metadata': metadata
            }
        }])
    except Exception:
        logger.exception('Failed to send event.')

@ftrack_connector_legacy.asynchronous.asynchronous
def _send_async_event(event_name, metadata=None):
    '''Call __send_event in a new thread.'''
    _send_event(event_name, metadata)


def send_event(event_name, metadata=None, asynchronous=True):
    '''Send usage event with *event_name* and *metadata*.

    If asynchronous is True, the event will be sent in a new thread.
    '''

    if asynchronous:
        _send_async_event(event_name, metadata)
    else:
        _send_event(event_name, metadata)
