#!/usr/bin/env python3

# Copyright (C) 2017-2019
#               Free Software Foundation, Inc.
# This file is part of Chisel
#
# Chisel is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# Chisel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Chisel; see the file COPYING.  If not, write to the
# Free Software Foundation, 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# Author Gaius Mulley <gaius.mulley@southwales.ac.uk>
#

import time
import socket
import sys
import os

from botbasic import basic


#
#  the purpose of the cache class is to replicate the functionality
#  in the basic class, but it attempts to look a value before using
#  a remote procedure call.
#
#  A number of these methods are not cached, but they are implemented
#  in the cache class so that the basic class can be completely hidden
#  from the higher level code.
#

class cache:
    #
    #  __init__ the cache constructor.
    #

    def __init__ (self, server, name):
        self._basic = basic (server, name)
        self._dict = {}

    #
    #  reset - delete all the cached values.
    #

    def reset (self):
        print("reset cache")
        self._dict = {}

    #
    #  getPenName - return the name of the pen map.
    #

    def getPenName (self):
        if 'getpenname' not in self._dict:
            self._dict['getpenname'] = self._basic.genPenName ()
        return self._dict['getpenname']

    #
    #  getpos - return the position of, obj in doom3 units.
    #

    def getpos (self, obj):
        l = 'getpos_%d' % (obj)
        if l not in self._dict:
            self._dict[l] = self._basic.getpos (obj)
        return self._dict[l]

    #
    #  me - return the bots entity, id.
    #

    def me (self):
        if 'me' not in self._dict:
            self._dict['me'] = self._basic.me ()
        return self._dict['me']

    #
    #  maxobj - return the maximum number of registered, ids in the game.
    #           Each monster, player, ammo pickup has an id
    #

    def maxobj (self):
        if 'maxobj' not in self._dict:
            self._dict['maxobj'] = self._basic.maxobj ()
        return self._dict['maxobj']

    #
    #  allobj - return a list of all objects
    #

    def allobj (self):
        return list(range(1, self.maxobj () + 1))

    #
    #  objectname - return the name of the object, d.
    #

    def objectname (self, d):
        l = "objectname %d\n" % (d)
        if l not in self._dict:
            self._dict[l] = self._basic.objectname (d)
        return self._dict[l]

    #
    #  isvisible - return True if object, d, is line of sight visible.
    #

    def isvisible (self, d):
        l = "isvisible %d\n" % (d)
        if l not in self._dict:
            self._dict[l] = self._basic.isvisible (d)
        return self._dict[l]

    #
    #  isfixed - return True if the object is a static fixture in the map.
    #

    def isfixed (self, d):
        l = "isfixed %d\n" % (d)
        if l not in self._dict:
            self._dict[l] = self._basic.isvisible (d)
        return self._dict[l]


    #
    #  timeout - if ticks < 0 then cancel any current timeout.
    #            if ticks >= 0 then initialise a timeout to occur
    #            at ticks frames in the future.  The timeout
    #            can be detected using the select method.
    #            The return value of timeout will be the remaining
    #            ticks to the previous timeout.
    #            A return value of -1 means the timeout was not
    #            active.  Any value >=0 is the remaining time before
    #            the timeout would expire.
    #

    def timeout (self, ticks):
        return self._basic.timeout (ticks)

    #
    #  right - step right at velocity, vel, for dist, units.
    #

    def right (self, vel, dist):
        self.delpos (self.me ())
        return self._basic.right (vel, dist)

    #
    #  forward - step forward at velocity, vel, for dist, units.
    #

    def forward (self, vel, dist):
        self.delpos (self.me ())
        return self._basic.forward (vel, dist)

    #
    #  left - step left at velocity, vel, for dist, units.
    #

    def left (self, vel, dist):
        return self.right (-vel, dist)

    #
    #  back - step back at velocity, vel, for dist, units.
    #

    def back (self, vel, dist):
        return self.forward (-vel, dist)

    #
    #  stepup - step up at velocity, vel, for dist, units.
    #

    def stepup (self, velocity, dist):
        return self._basic.stepup (velocity, dist)

    #
    #  stepvec - step forward at velocity, velforward and velright for
    #            dist, units.
    #

    def stepvec (self, velforward, velright, dist):
        self.delpos (self.me ())
        return self._basic.stepvec (velforward, velright, dist)

    #
    #  sync - wait for any event to occur.
    #         The event will signify the end of
    #         move, fire, turn, reload action.
    #

    def sync (self):
        self.delpos (self.me ())
        return self._basic.sync ()

    #
    #  select - wait for any event:  legal events are
    #           ['move', 'fire', 'turn', 'reload', 'timeout'].
    #

    def select (self, l):
        # self.delpos (self.me ())
        return self._basic.select (l)


    #
    #  startFiring - fire weapon
    #                It returns the amount of ammo left.
    #

    def startFiring (self):
        self.delammo ()
        return self._basic.startFiring ()

    #
    #  stop_firing - stop firing weapon
    #                It returns the amount of ammo left.
    #

    def stopFiring (self):
        self.delammo ()
        return self._basic.stopFiring ()

    #
    #  reloadWeapon - reload the current weapon
    #                 It returns the amount of ammo left.
    #

    def reloadWeapon (self):
        return self._basic.reloadWeapon ()

    #
    #  inventoryWeapon - return True if bot has the weapon.
    #                    Note that without ammo the bot cannot
    #                    change to this weapon.
    #

    def inventoryWeapon (self, weapon_number):
        return self._cache.inventoryWeapon (weapon_number)


    #
    #  dropWeapon - returns True if the current weapon was dropped.
    #

    def dropWeapon (self):
        return self._cache.dropWeapon ()


    #
    #  ammo - returns the amount of ammo for the weapon_number.
    #

    def ammo (self, weapon_number):
        keystr = 'ammo %d' % weapon_number
        if keystr not in self._dict:
            self._dict[keystr] = self._basic.ammo (weapon_number)
        return self._dict[keystr]

    #
    #  aim - aim weapon at player_number
    #

    def aim (self, player_number):
        print("cache aim")
        return self._basic.aim (player_number)

    #
    #  angle - return the angle the bot is facing.
    #          The angle returned is a penguin tower angle.
    #          0 up, 180 down, 90 left, 270 right.
    #          Equivalent to the doom3 Yaw.
    #

    def angle (self):
        if 'angle' not in self._dict:
            self._dict['angle'] = self._basic.angle ()
        return self._dict['angle']

    #
    #  turn - turn to face, angle.
    #

    def turn (self, angle, angle_vel):
        self.delpos (self.me ())
        return self._basic.turn (angle, angle_vel)

    #
    #  delpos - deletes the cached entry for position of object, i.
    #

    def delpos (self, i):
        l = 'getpos_%d' % (i)
        self._dict.pop (l, None)

    #
    #  delammo - deletes the cached entry of ammo.
    #

    def delammo (self):
        self._dict.pop ('ammo', None)

    #
    #  inventoryWeapon - return True if bot has the weapon.
    #                    Note that without ammo the bot cannot
    #                    change to this weapon.
    #

    def inventoryWeapon (self, weapon_number):
        if 'inventoryweapon' not in self._dict:
            self._dict['inventoryweapon'] = self._basic.inventoryWeapon (weapon_number)
        return self._dict['inventoryweapon']

    #
    #  changeWeapon - attempts to change to weapon_number.
    #                 If successful the amount of ammo is returned
    #                 else -1 is returned.
    #

    def changeWeapon (self, weapon_number):
        return self._basic.changeWeapon (weapon_number)

    #
    #  dropWeapon - returns True if the current weapon was dropped.
    #

    def dropWeapon (self):
        return self._basic.dropWeapon ()

    #
    #  getPenMapName - return the name of the current pen map.
    #

    def getPenMapName (self):
        if 'getpenmapname' not in self._dict:
            self._dict['getpenmapname'] = self._basic.getPenMapName ()
        return self._dict['getpenmapname']

    #
    #  getTag - returns the tag value in the map file.
    #

    def getTag (self, name):
        tagname = "tag " + name
        if tagname not in self._dict:
            self._dict[tagname] = self._basic.getTag (name)
        return self._dict[tagname]

    #
    #  getPlayerStart - return the player start location.
    #

    def getPlayerStart (self):
        if 'info_player_start' not in self._dict:
            self._dict['info_player_start'] = self._basic.getPlayerStart ()
        return self._dict['info_player_start']


    #
    #  getEntityNo - return the entity number which contains the
    #                pair of strings left, right.
    #

    def getEntityNo (self, left, right):
        name = "entitynamed %s %s" % (left, right)
        if name not in self._dict:
            self._dict[name] = self._basic.getEntityNo (left, right)
        return self._dict[name]


    #
    #  getEntityPos - return the spawn position of entity_no in the static doom3 map.
    #                 The return result is a doom3 [x, y, z] coordinate.
    #

    def getEntityPos (self, entity_no):
        name = "entity %d" % entity_no
        if name not in self._dict:
            self._dict[name] = self._basic.getEntityPos (entity_no)
        return self._dict[name]

    #
    #  getSpawnPos - return the doom3 [x, y, z] of this bots spawn location.
    #

    def getSpawnPos (self):
        return self.getEntityPos (self.me ())

    #
    #  getEntityName - returns the name string for, entity_no.
    #

    def getEntityName (self, entity_no):
        name = "entity name %d" % entity_no
        if name not in self._dict:
            self._dict[name] = self._basic.getEntityName (entity_no)
        return self._dict[name]

    #
    #  turn the visibility shader on/off.  value is a boolean.
    #

    def visibilityFlag (self, value):
        return self._basic.visibilityFlag (value)

    #
    #  visibility - assign the alpha value to tbe visibility shader.
    #               a value between 0.0 and 1.0 detemines whether
    #               the object is transparent 0.0 to non transparent 1.0.
    #

    def visibility (self, red, green, blue, alpha):
        return self._basic.visibility (red, green, blue, alpha)

    #
    #  visibilityParams -
    #

    def visibilityParams (self, parameters):
        return self._basic.visibilityParams (parameters)

    #
    #  flipVisibility - flip the visibility shader buffer.
    #

    def flipVisibility (self):
        return self._basic.flipVisibility ()

    #
    #  getselfentitynames - returns a list of names associated with the bot.
    #

    def getselfentitynames (self):
        name = "selfentitynames"
        if name not in self._dict:
            self._dict[name] = self._basic.getselfentitynames ()
        return self._dict[name]

    #
    #  setvisibilityshader - allows the bot to change its visibility shader.
    #                        It can change the visibility shader of different entities
    #                        which it owns.  For example weapon, head, body can be given
    #                        different shaders if required.
    #

    def setvisibilityshader (self, shader, entitylist = []):
        return self._basic.setvisibilityshader (shader, entitylist)

    #
    #  init_bbox - create a bounded box and return its id.
    #              bbox_origin is the bottom left hand corner in the doom3 universe.
    #              bbox_size is the size of the bounded box in doom3 units.
    #

    def init_bbox (self, bbox_origin, bbox_size):
        return self._basic.init_bbox (bbox_origin, bbox_size)

    #
    #  delete_bbox - destroy the bbox_id.
    #

    def delete_bbox (self, bbox_id):
        return self._basic.delete_bbox (bbox_id)

    #
    #  delete_bbox_all - destroy all bboxes for this bot on the doom3 server.
    #

    def delete_bbox_all (self):
        self._basic.delete_bbox_all ()

    #
    #  bbox_track - track bbox_id for ticks.  Return
    #               -1 if the bbox_id cannot be tracked,
    #               -1 indicates that the bbox_id is no
    #               longer visible.
    #               The bbox_track does not block.

    def bbox_track (self, bbox_id, ticks):
        return self._basic.bbox_track (bbox_id, ticks)

    #
    #  track - track entity_num for ticks.  Return
    #          -1 if the entity_num cannot be tracked,
    #          -1 indicates that the entity_num is no
    #          longer visible.
    #          track does not block.
    #

    def track (self, entity_num, ticks):
        return self._basic.track (entity_num, ticks)

    #
    #  bbox_include_collision - enable the collision attribute of a bbox_list and
    #                           returns true if successful.
    #                           bbox_list can be "all" or ["all"] which includes all
    #                           boxes visibility attributes.
    #

    def bbox_include_collision (self, bbox_list):
        return self._basic.bbox_include_collision (bbox_list)

    #
    # bbox_exclude_collision -  disable the collision attribute of a bbox_list and
    #                           return the bbox_list if successful.
    #                           bbox_list can be "all" or ["all"] which excludes all
    #                           boxes collision attributes.
    #

    def bbox_exclude_collision (self, bbox_list):
        return self._basic.bbox_exclude_collision (bbox_list)

    #
    #  bbox_include_visibility - enable the visibility attribute bbox_list and
    #                            returns true if successful.
    #                            bbox_list can be "all" or ["all"] which includes all
    #                            boxes visibility attributes.
    #

    def bbox_enable_visibility (self, bbox_list):
        return self._basic.bbox_enable_visibilty (bbox_list)

    #
    #  bbox_exclude_visibility - disable the visibility attribute of a bbox_list and
    #                            return the bbox_list if successful.
    #                            bbox_list can be "all" or ["all"] which excludes all
    #                            boxes visibility attributes.
    #

    def bbox_exclude_visibility (self, bbox_list):
        return self._basic.bbox_exclude_visibility (bbox_list)
