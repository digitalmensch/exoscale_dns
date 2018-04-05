#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `exoscale_dns` package."""

import exoscale_dns
import pytest
import os
import time


################################################################################
# Fixtures
################################################################################

@pytest.fixture
def access_key():
    return exoscale_dns.access_key(
        os.environ.get('APIKEY', 'invalid'),
        os.environ.get('SECRET', 'invalid')
    )

@pytest.fixture
def test_domain(access_key):
    for domain in access_key:
        if domain.name == os.environ.get('DOMAIN', 'invalid'):
            yield domain
            break
            try:
                domain.delete()
            except:
                pass
    else:
        domain = access_key.create(os.environ.get('DOMAIN', 'invalid'))
        yield domain
        try:
            domain.delete()
        except:
            pass


@pytest.fixture
def test_record(test_domain):
    for record in test_domain:
        if record.name.startswith('test'):
            return record
    return test_domain.add_record(f'test{int(time.time())}', 'TXT', 'test')


################################################################################
# Tests for `access_key`
################################################################################

def test_create_access_key(access_key):
    assert access_key is not None

def test_list_all_domains(access_key):
    for domain in sorted(access_key):
        assert isinstance(domain, exoscale_dns.domain)


################################################################################
# Tests for `domain`
################################################################################

def test_create_test_domain(test_domain):
    assert test_domain is not None

def test_list_all_records(test_domain):
    for record in test_domain:
        assert isinstance(record, exoscale_dns.record)

def test_fetch_zone_file(test_domain):
    zone = test_domain.zone()
    assert isinstance(zone, str)
    assert len(zone) > 0

def test_delete_domain(test_domain, access_key):
    assert test_domain.delete() is None
    time.sleep(5)
    for domain in access_key:
        assert domain.name != test_domain.name



################################################################################
# Tests for `record`
################################################################################

def test_add_record(test_domain):
    record = test_domain.add_record(f'test{int(time.time())}', 'TXT', 'test')
    assert isinstance(record, exoscale_dns.record)

def test_update_record(test_record):
    record2 = test_record.update(content=f'{time.time()}')
    assert test_record.content != record2.content
    assert test_record.id == record2.id

def test_delete_record(test_record, test_domain):
    assert test_record.delete() is None
    time.sleep(5)
    for record in test_domain:
        assert record.name != test_record.name
