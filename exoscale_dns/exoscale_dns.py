# -*- coding: utf-8 -*-

"""Main module."""

import attr
import requests

@attr.s(slots=True, frozen=True)
class access_key(object):
    api_key = attr.ib()
    secret = attr.ib(repr=False)

    def __iter__(self):
        ''' List all domains. '''
        response = requests.get(
            f'https://api.exoscale.ch/dns/v1/domains',
            headers = {
                'X-DNS-Token': f'{self.api_key}:{self.secret}',
                'Accept': 'application/json'
            }
        ).json()
        for domain_details in response:
            domain_details = domain_details['domain']
            yield domain(self, **domain_details)

    def create(self, name):
        ''' Create a domain. '''
        response = requests.post(
            f'https://api.exoscale.ch/dns/v1/domains',
            headers = {
                'X-DNS-Token': f'{self.api_key}:{self.secret}',
                'Accept': 'application/json'
            },
            json = {
                'domain': {'name': name}
            }
        ).json()
        domain_details = response['domain']
        return domain(self, **domain_details)


@attr.s(slots=True, frozen=True)
class domain(object):
    _access_key = attr.ib(repr=False)
    id = attr.ib()
    user_id = attr.ib()
    registrant_id = attr.ib()
    account_id = attr.ib()
    name = attr.ib()
    unicode_name = attr.ib()
    token = attr.ib(repr=False)
    state = attr.ib()
    lockable = attr.ib()
    auto_renew = attr.ib()
    whois_protected = attr.ib()
    record_count = attr.ib()
    service_count = attr.ib()
    expires_on = attr.ib()
    created_at = attr.ib()
    updated_at = attr.ib()

    def __iter__(self):
        ''' List all records. '''
        response = requests.get(
            f'https://api.exoscale.ch/dns/v1/domains/{self.name}/records',
            headers = {
                'X-DNS-Domain-Token': self.token,
                'Accept': 'application/json'
            }
        ).json()
        for record_details in response:
            record_details = record_details['record']
            yield record(self, **record_details)

    def add_record(self, name, record_type, content, ttl=None, prio=None):
        ''' Add a new record. '''
        data = {
            'record': {
                'name': name,
                'record_type': record_type,
                'content': content
            }
        }
        if ttl: data['record']['ttl'] = ttl
        if prio: data['record']['prio'] = prio
        response = requests.post(
            f'https://api.exoscale.ch/dns/v1/domains/{self.name}/records',
            headers = {
                'X-DNS-Domain-Token': self.token,
                'Accept': 'application/json'
            },
            json = data
        ).json()
        record_details = response.get('record', None)
        if not record_details:
            raise Exception(str(response))
        return record(self, **record_details)

    def delete(self):
        ''' Delete this domain. '''
        response = requests.delete(
            f'https://api.exoscale.ch/dns/v1/domains/{self.name}',
            headers = {
                'X-DNS-Token': f'{self._access_key.api_key}:{self._access_key.secret}',
                'Accept': 'application/json'
            }
        ).json()
        if response != {}:
            raise Exception(str(response))
        return None

    def zone(self):
        ''' Fetch zone file for this domain. '''
        response = requests.get(
            f'https://api.exoscale.ch/dns/v1/domains/{self.name}/zone',
            headers = {
                'X-DNS-Domain-Token': self.token,
                'Accept': 'application/json'
            }
        ).json()
        zone = response.get('zone', None)
        if not zone:
            raise Exception(str(response))
        return zone

@attr.s(slots=True, frozen=True)
class record(object):
    _domain = attr.ib(repr=False)
    id = attr.ib()
    domain_id = attr.ib()
    parent_id = attr.ib()
    name = attr.ib()
    content = attr.ib()
    ttl = attr.ib()
    prio = attr.ib()
    record_type = attr.ib()
    system_record = attr.ib()
    created_at = attr.ib()
    updated_at = attr.ib()

    def update(self, name=None, content=None, ttl=None, prio=None):
        data = {}
        if name: data['name'] = name
        if content: data['content'] = content
        if ttl: data['ttl'] = ttl
        if prio: data['prio'] = prio
        response = requests.put(
            f'https://api.exoscale.ch/dns/v1/domains/{self._domain.name}/records/{self.id}',
            headers = {
                'X-DNS-Domain-Token': self._domain.token,
                'Accept': 'application/json'
            },
            json = data
        ).json()
        record_details = response.get('record', None)
        if not record_details:
            raise Exception(str(response))
        return record(self._domain, **record_details)

    def delete(self):
        response = requests.delete(
            f'https://api.exoscale.ch/dns/v1/domains/{self._domain.name}/records/{self.id}',
            headers = {
                'X-DNS-Domain-Token': self._domain.token,
                'Accept': 'application/json'
            }
        ).json()
        if response != {}:
            raise Exception(str(response))
        return None
