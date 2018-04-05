#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `exoscale_dns` package."""

import exoscale_dns
import pytest
import os
import time


@pytest.fixture
def access_key():
    return exoscale_dns.access_key(
        os.environ.get('APIKEY'),
        os.environ.get('SECRET')
    )


def test_create_access_key(access_key):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    assert access_key is not None

def test_list_all_domains(access_key):
    for domain in sorted(access_key):
        assert isinstance(domain, exoscale_dns.domain)

def test_list_all_records(access_key):
    for domain in sorted(access_key):
        for record in domain:
            assert isinstance(record, exoscale_dns.record)
        break

def test_fetch_zone_file(access_key):
    for domain in sorted(access_key):
        zone = domain.zone()
        assert isinstance(zone, str)
        assert len(zone) > 0
        break

def test_add_record(access_key):
    for domain in sorted(access_key):
        record = domain.add_record(f'test{int(time.time())}', 'TXT', 'test')
        assert isinstance(record, exoscale_dns.record)
        break

def test_update_record(access_key):
    for domain in sorted(access_key):
        for record in domain:
            if record.name.startswith('test'):
                record2 = record.update(content=f'{time.time()}')
                assert record.content != record2.content
                assert record.id == record2.id
        break

def test_delete_record(access_key):
    for domain in sorted(access_key):
        for record in domain:
            if record.name.startswith('test'):
                assert record.delete() == None
        break

def test_create_delete_domain(access_key):
    name = f'test-domain-{int(time.time())}.ch'
    domain = access_key.create(name)
    assert isinstance(domain, exoscale_dns.domain)
    domain.delete()
    time.sleep(3)
    for d in list(access_key):
        assert d.name != name
