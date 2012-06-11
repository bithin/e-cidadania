#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010-2012 Cidadania S. Coop. Galega
#
# This file is part of e-cidadania.
#
# e-cidadania is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# e-cidadania is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with e-cidadania. If not, see <http://www.gnu.org/licenses/>.

import httplib

from django.contrib.auth.models import User

from django.test import Client
from django.test import TestCase

from tests.data_seeder import seeder


class ECDTestCase(TestCase):
    """Class which extends Django TestCase and adds methods specific to 
    e-cidadania for testing.
    """
    
    def init(self):
        """Performs set up for the tests.
        """
        
        self.client = Client(enforce_csrf_checks=True)
    
    def seed(self, model, properties=None, constraints=None, follow_fk=None, 
             generate_fk=None, follow_m2m=None, factory=None, commit=True):
        """Generates and returns a new instance of the `model` with 
        properties in `properties`.
        """
        instance = seeder.seed(model=model, constraints=constraints, 
                               follow_fk=follow_fk, generate_fk=None, 
                               follow_m2m=None, factory=None,
                               model_properties=properties, commit=commit)
        
        return instance
    
    def seedn(self, count, model, properties, constraints=None, follow_fk=None, 
              generate_fk=None, follow_m2m=None, factory=None, commit=True):
        """Generates and returns `count` number of instances of `model` with
        properties in `properties`.
        """
        
        obj_list = seeder.seedn(count=count, model=model, constraints=constraints,
                                follow_fk=follow_fk, generate_fk=generate_fk,
                                follow_m2m=follow_m2m, factory=factory,
                                model_properties=properties, commit=True)
        return obj_list
    
    def create_user(self, username, password, email=None, properties=None):
        """Creates, saves and returns a user with a given username, password
        and email. If `properties` is supplied, it will be applied to the 
        created user.
        """
        
        user = User.objects.create_user(username, password, email)
        
        if properties:
            for key in properties:
                setattr(user, key, properties[key])
            user.save()
        return user
    
    def login(self, username, password, email=None):
        """Logs in a user with the given username and password. If the user is 
        not present in the database, it will be created and logged in.
        
        We assume `username` is unique across the database.
        """
        
        try:
            user = User.objects.get(username=username)
        except Exception:
            user = None
        if user is None:
            user = self.create_user(username, password, email)
        
        self.client.login(username=username, password=password)
    
    def logout(self):
        """Logs out the currently logged in user.
        """
        
        self.client.logout()
    
    def isLoggedIn(self, user=None):
        """Checks and returns True if a user is logged in otherwise returns
        False.
        """
        
        if '_auth_user_id' not in self.client.session:
            return False
        
        if (user.pk == self.client.session['_auth_user_id']):
            return True
    
        return False
        
    def get(self, url, data={}, follow=False, **extra):
        """
        Performs a get to the given url and returns the response.
        """
        
        response = self.client.get(url, data=data, follow=follow, extra=extra)
        return response
    
    def post(self, url, data={}, content_type, follow=False, **extra):
        """
        Performs a post to the supplied url and returns the response.
        """
        
        response = self.client.post(path=url, data=data, content_type=content_type,
                                    follow=follow, extra=extra)
        return response
    
    def printResponse(self):
        """Prints response.
        """
        pass
    
    
    def assertResponseCode(self, response, status_code):
        """Asserts that the response status is status_code.
        """
        if response.status_code != status_code:
            verbose_codes = [
            httplib.FOUND,
            ]
            message_codes = [
            httplib.FORBIDDEN, httplib.BAD_REQUEST, httplib.NOT_FOUND,
            ]
            url_codes = [httplib.NOT_FOUND]
            
            if response.status_code in verbose_codes:
                print response

            if response.context and response.status_code in message_codes:
                try:
                    print response.context['message']
                except KeyError:
                    pass
    
            if response.status_code in url_codes:
                print response.request['PATH_INFO']

        self.assertEqual(status_code, response.status_code)

    def assertResponseOK(self, response):
        """Asserts that the response status is OK.
        """
        self.assertResponseCode(response, httplib.OK)

    def assertResponseRedirect(self, response):
        """Asserts that the response status is FOUND.
        """
        self.assertResponseCode(response, httplib.FOUND)

    def assertResponseForbidden(self, response):
        """Asserts that the response status is FORBIDDEN.
        """
        self.assertResponseCode(response, httplib.FORBIDDEN)

    def assertResponseBadRequest(self, response):
        """Asserts that the response status is BAD_REQUEST.
        """
        self.assertResponseCode(response, httplib.BAD_REQUEST)

    def assertResponseNotFound(self, response):
        """Asserts that the response status is NOT_FOUND.
        """
        self.assertResponseCode(response, httplib.NOT_FOUND)