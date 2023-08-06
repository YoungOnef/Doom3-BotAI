#!/usr/bin/env python3

# Copyright (C) 2017-2022
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
import random

from botaa import aas
from botbasic import basic
from botcache import cache
from chvec import *
from math import atan2, sqrt

debugging = False
debugBulk = False

pen2doom3units = 48   # inches per ascii square
angle_offset = 0
diagonal_scaling = 0.55
vertical_horizontal_scaling = 0.55


#
#  sqr - return the square of x.
#

def sqr (x):
    return x * x


#
#  incAngle - increments, angle, by, inc, ensuring it stays within 0..359 degrees.
#

def incAngle (angle, inc):
    angle += inc
    while angle < 0:
        angle += 360
    angle %= 360
    return angle


#
#  callScaleOffset - Pre-conditions:  pen0 and pen1 are pen coordinates
#                                     doom0 and doom1 are doom3 coordinates.
#                                     Two objects are specified in 0 and 1.
#                    Post-condition:  this function returns the scaleX, offsetX
#                                     and scaleY and offsetY to transform
#                                     a coordinate in doom3 to a pen coordinate.
#

def calcScaleOffset (pen0, doom0, pen1, doom1):
    diffPen = subVec (pen0, pen1)
    print ("pen0 =", pen0)
    print ("pen1 =", pen1)
    print ("diffPen =", diffPen)
    diffD3 = subVec (doom0, doom1)
    print ("doom0 =", doom0)
    print ("doom1 =", doom1)
    print ("diffD3 =", diffD3)
    scaleX = float (diffD3[0]) / float (diffPen[0])
    scaleY = float (diffD3[1]) / float (diffPen[1])
    offsetX = doom0[0] - float (pen0[0]) * scaleX
    offsetY = doom0[1] - float (pen0[1]) * scaleY
    return scaleX, offsetX, scaleY, offsetY


#
#  signOf - if X is positive return 1 else return -1.
#

def signOf (x):
    if x >= 0:
        return 1
    return -1


class bot:
    #
    #  __init__ the constructor for bot class which
    #           joins together all the lower layers in the AI
    #

    def __init__ (self, server, name):
        self._cache = cache (server, name)
        self._aas = aas (self.getPenMapName ())
        self._id = self.me ()
        penMin, penMax, doomMin, doomMax = self.getLimits ()
        spawnPenPlayer = intVec (self._aas.getPlayerStart ())
        spawnD3Player = intVec (self._cache.getPlayerStart ())
        spawnD3Python = intVec (self._cache.getSpawnPos ())
        self._name = self._cache.getEntityName (self._id)
        spawnPenPython = intVec (self._aas.getSpawnFromName ("python_doommarine_mp"))
        print ("spawnPenPython =", spawnPenPython)
        self._scaleX, self._offsetX, self._scaleY, self._offsetY = calcScaleOffset (penMin, doomMin, penMax, doomMax)
        print (self._scaleX, self._offsetX, self._scaleY, self._offsetY)
        print ("the doom3 coordinate", spawnD3Player, "really maps onto", spawnPenPlayer)
        self._scale2DX = signOf (self._scaleX)
        self._scale2DY = signOf (self._scaleY)
        print ("the 2D doom scale units are", self._scale2DX, "and", self._scale2DY)
        test = self.d2pv (spawnD3Player)
        print ("the doom3 coordinate", spawnD3Python, "really maps onto", spawnPenPython)
        print ("the doom3 coordinate", spawnD3Player, "really maps onto", spawnPenPlayer)
        print ("asserting spawn player coordinates on pen and doom3 maps match: ", end="")
        assert (equVec (self.d2pv (spawnD3Player), spawnPenPlayer))
        print ("passed")
        print ("asserting spawn position of doom python bot coordinates on pen and doom3 maps match: ", end="")
        #
        # this assert will only work for a single python bot
        #
        # assert (equVec (self.d2pv (spawnD3Python), spawnPenPython))
        # print ("passed")
        print ("reversing transform d2pv (", spawnPenPython, ") ->", self.p2dv (spawnPenPython), " == ", spawnD3Python)
        # os.sys.exit (0)

    #
    #  getLimits -
    #

    def getLimits (self):
        return [[float (self.getTag ("penminx")), float (self.getTag ("penminy"))],
                [float (self.getTag ("penmaxx")), float (self.getTag ("penmaxy"))],
                [float (self.getTag ("doomminx")), float (self.getTag ("doomminy"))],
                [float (self.getTag ("doommaxx")), float (self.getTag ("doommaxy"))]]

    #
    #  getPenMapName - return the name of the pen map.
    #

    def getPenMapName (self):
        return self._cache.getPenMapName ()


    #
    #  getTag - returns the tag value in the map file.
    #

    def getTag (self, name):
        return self._cache.getTag (name)


    #
    #  get_label_list - returns a list of all user defined labels used in the map.
    #

    def get_label_list (self):
        return self._aas.get_label_list ()


    #
    #  me - return the bots entity, id.
    #

    def me (self):
        self._aas.printFloor ()
        return self._cache.me ()

    #
    #  maxobj - return the maximum number of registered, ids in the game.
    #           Each monster, player, ammo pickup has an id
    #

    def maxobj (self):
        return self._cache.maxobj ()

    #
    #  allobj - return a list of all objects
    #

    def allobj (self):
        return self._cache.allobj ()


    #
    #  all_monsters - return a list of all monsters.
    #

    def all_monsters (self):
        return []

    #
    #  all_players - return a list of all players (bots and human).
    #

    def all_players (self):
        return self.all_human_players () + self.all_bot_players ()

    #
    #  all_human_players - return a list of all human players.
    #

    def all_human_players (self):
        return []  # --fixme-- finish this gaius

    #
    #  all_bot_players - return a list of all bot players.
    #

    def all_bot_players (self):
        return []  # --fixme-- finish this gaius

    #
    #  all_bot_monsters - return a list of all bot monsters.
    #

    def all_bot_monsters (self):
        return []  # --fixme-- finish this gaius


    def all_ammo_pickups (self):
        return []  # --fixme-- finish this gaius


    def all_weapon_pickups (self):
        return []  # --fixme-- finish this gaius

    #
    #  get_current_room - return the current room in which the bot resides.
    #

    def get_current_room (self):
        return 0  # --fixme-- finish this gaius

    #
    #  get_doors - return the list of doors for the current room if room_no is None
    #              or the particular room specified.
    #

    def get_doors (self, room_no = None):
        return [ ]   # --fixme-- finish this gaius

    #
    #  getpos - return the position of, obj in doom3 units.
    #

    def getpos (self, obj):
        p = self._cache.getpos (obj)
        return [p[0], p[1], p[2]]

    #
    #  stepup -
    #

    def stepup (self, velocity, dist):
        return self._cache.stepup (velocity, dist)

    #
    #  crouch -
    #

    def crouch (self):
        return self.stepup (-2, 4*12)

    #
    #  forward - step forward at velocity, for dist, units.
    #

    def forward (self, velocity, dist):
        return self._cache.forward (velocity, dist)

    #
    #  back - step back at velocity, for dist, units.
    #

    def back (self, velocity, dist):
        return self._cache.back (velocity, dist)

    #
    #  left - step left at, velocity, for dist, units.
    #

    def left (self, velocity, dist):
        return self._cache.left (velocity, dist)

    #
    #  right - step right at velocity, for dist, units.
    #

    def right (self, velocity, dist):
        return self._cache.right (velocity, dist)

    #
    #  atod3 - convert a penguin tower map angle into the doom3 angle.
    #

    def atod3 (self, angle):
        return incAngle (angle, angle_offset)

    #
    #  turn - turn to face, angle.  The angle is a penguin tower angle.
    #         0 up, 180 down, 90 left, 270 right.
    #

    def turn (self, angle, angle_velocity):
        return self._cache.turn (self.atod3 (angle), angle_velocity)

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
        return self._cache.timeout (ticks)

    #
    #  select - wait for any desired event:  legal events are
    #           ['move', 'fire', 'turn', 'reload', 'timeout',
    #            'track', 'bbox_visible', 'bbox_touch'].
    #

    def select (self, l):
        return self._cache.select (l)

    #
    #  sync - wait for any event to occur.
    #         The event will signify the end of
    #         move, fire, turn, reload action.
    #

    def sync (self):
        return self._cache.sync ()

    #
    #  angle - return the angle the bot is facing.
    #          The angle returned is a penguin tower angle.
    #          0 up, 180 down, 90 left, 270 right.
    #          Equivalent to the doom3 Yaw.
    #

    def angle (self):
        return self._cache.angle ()

    #
    #  calcnav - calculate the navigation route between us and object, d.
    #            No movement is done, it only works out the best route.
    #            This is quite expensive and should be used sparingly.
    #            It returns the total distance between ourself and
    #            object, d, assuming this route was followed.  Notice
    #            this is not the same as a line of sight distance.
    #            The distance returned is in penguin tower units.
    #            None is returned if the bot is unable to find a route
    #            (or it considers itself on a wall).
    #

    def calcnav (self, d):
        self.reset ()
        src = self.d2pv (self.getpos (self.me ()))
        dest = self.d2pv (self.getpos (d))
        return self._aas.calcnav (src, dest)


    #
    #  calcnav_pos - calculate the navigation route between us and position, dest.
    #                No movement is done, it only works out the best route.
    #                This is quite expensive and should be used sparingly.
    #                It returns the total distance between ourself and
    #                dest, assuming this route was followed.  Notice
    #                this is not the same as a line of sight distance.
    #                The distance returned is in penguin tower units
    #                or None is returned if the bot considers itself to be on a wall.
    #

    def calcnav_pos (self, dest):
        self.reset ()
        src = self.d2pv (self.getpos (self.me ()))
        return self._aas.calcnav (src, dest)


    #
    #  calcAngle - calculate the angle to face vector, v.
    #

    def _calcAngle (self, v):
        if v[0] == 0:
            if debugging:
                print("short cut, not using atan2 north/south", end=' ')
            if v[1] > 0:
                angle = 270
            else:
                angle = 90
        elif v[1] == 0:
            if debugging:
                print("short cut, not using atan2 left/right", end=' ')
            if v[0] > 0:
                angle = 180
            else:
                angle = 0
        else:
            if debugging:
                print("using atan2", end=' ')
            angle = incAngle (int (atan2 (float (v[1]), float (v[0])) * 180.0 / 3.1415927), 180)   # radians into degrees

        if debugging:
            print("angle =", angle)
        return angle

    #
    #  turnface - turn and face vector.  The vec_doom _must_ be a doom vector.
    #

    def turnface (self, vec_doom, velocity = None):
        if debugging:
            print("vec_doom =", vec_doom, end=' ')
        angle = self._calcAngle (vec_doom)
        if velocity == None:
            #
            #  we work out the quickest anti/clock turn to achieve correct orientation.
            #
            old = self.angle ()
            if old < angle:
                if abs (old + 360 - angle) < abs (angle - old):
                    self.turn (angle, -1)  # quicker to turn using -1
                else:
                    self.turn (angle, 1)  # quicker to turn using 1
            else:
                if abs (angle + 360 - old) < abs (angle - old):
                    self.turn (angle, 1)  # quicker to turn using 1
                else:
                    self.turn (angle, -1)  # quicker to turn using -1
        else:
            self.turn (angle, velocity)


    #
    #  d2pv - convert a doom3 coordinate [x, y, z] into a penguin tower coordinate.
    #         converted vector [p, q] is returned.
    #

    def d2pv (self, v):
        result = []
        if len (v) > 1:
            t = (float (v[0]) - self._offsetX) / self._scaleX
            result = [t]
            t = (float (v[1]) - self._offsetY) / self._scaleY
            result += [t]
        return intVec (result)


    def midPen2Doom (self, p):
        return [p[0] * pen2doom3units + self._scale2DX * pen2doom3units/2,
                p[1] * pen2doom3units + self._scale2DY * pen2doom3units/2]

    #
    #  p2d - in:   a penguin tower unit.
    #        out:  return a d3 unit.
    #

    def p2d (self, u):
        if u is None:
            return None
        return pen2doom3units * u

    #
    #  on_pen - in:  an object and a pen_coord
    #           out:  True if the object is not None and it resides on pen_coord.
    #

    def on_pen (self, obj, pen_coord):
        return (obj != None) and (equVec (pen_coord, self.d2pv (self.getpos (obj))))

    #
    #  journey - move at velocity, for a distance_pen.
    #            along the navigation route calculated in calcnav.
    #            Post-condition:  the bot is moved along the journey route.
    #                    0 is returned if the bot has reached destination_pen.
    #                    1 is returned if the bot has reached an intemediate hop.
    #                    2 is returned if the bot has fallen off the route.
    #                    3 is returned if the obj has moved.
    #                    4 run out of allowable distance_pen steps.
    #                    5 none of the above
    #

    def journey (self, velocity, distance_pen, destination_pen, obj = None):
        self.reset ()
        if debugging:
            print ("journey along route", self._aas._route)
        if obj is None:
            initial_obj_pen = None
        else:
            initial_obj_pen = self.d2pv (self.getpos (obj))  # if object moves off this grid square we early return
        distance_doom = self.p2d (distance_pen) # convert to doom3 unit
        self._aas._skipPos (self.d2pv (self.getpos (self.me ())))
        if debugging:
            print ("aas.getHop (0) =", self._aas.getHop (0), "my pos =", self.d2pv (self.getpos (self.me ())), "destination_pen =", destination_pen)
            print ("distance_pen =", distance_pen)
        #
        #  keep stepping along route as long as the object does not move and we have dist units to move along
        #
        while (distance_pen > 0) and (velocity != 0) and self.on_pen (obj, initial_obj_pen) and (not equVec (self._aas.getHop (0), destination_pen)):
            if debugging:
                print ("while loop: distance_pen =", distance_pen)
            v = subVec (self.d2pv (self.getpos (self.me ())), self._aas.getHop (0))
            hopPos = self._aas.getHop (0)
            hops = 1
            while (hops < self._aas.noOfHops ()) and equVec (subVec (hopPos, self._aas.getHop (hops)), v):
                hopPos = self._aas.getHop (hops)
                hops += 1
            if debugging:
                print("bulk hop nav", self._aas.getHop (hops-1), hops)
                print("aas._route = ", self._aas._route)
            distance_pen = self.ssBulkNav (velocity, self._aas.getHop (hops-1), hops)
            if debugging:
                print("bulk hop nav: distance_pen =", distance_pen)
            if distance_pen > 0:
                self.reset ()
                mypos = self.d2pv (self.getpos (self.me ()))
                for h in range (hops):
                    if equVec (mypos, self._aas.getHop (h)):
                        for i in range (h):
                            self._aas.removeHop (0, self._aas.getHop (0))
                        hops = 0  #  use first hop as we have discarded hops 0..h-1
                        self._aas._skipPos (self.d2pv (self.getpos (self.me ())))
                        break
                    else:
                        if debugging:
                            print("oops fallen off the route, aborting and will try again")
                        return 2   # off the route
                if debugging:
                    print("new journey route", self._aas._route)
        if debugging:
            print ("destination_pen =", destination_pen)
        if equVec (destination_pen, self.d2pv (self.getpos (self.me ()))):
            if debugging:
                print("journey algorithm reached the goal object")
            return 0  # reached destination
        elif equVec (self._aas.getHop (0), destination_pen):
            if debugging:
                print ("journey algorithm reached intemediate hop")
            return 1  # reached intermediate hop
        elif distance_pen == 0:
            if debugging:
                print ("journey algorithm ran out of distance")
            return 4  # run out of distance
        elif not self.on_pen (obj, initial_obj_pen):
            return 3  # obj has moved
        else:
            if debugging:
                print ("journey algorithm failed")
        self.reset ()
        return 5  # none of the above


    def runArc (self, angle, dist):
        self.forward (100, dist)
        self.turn (angle, 1)
        self.select (["move"])
        self.select (["turn"])


    #
    #  ssBulkNav - multiple square navigate, turn and move to position.
    #

    def ssBulkNav (self, velocity, position_pen, noHops):
        if debugBulk:
            print ("ssBulkNav (velocity =", velocity, "position_pen =", position_pen, "noHops =", noHops)
        self.reset ()
        initpos_doom = self.getpos (self.me ())
        initpos_pen = self.d2pv (initpos_doom)
        if equVec (position_pen, initpos_pen):
            if debugBulk:
                print ("ssBulkNav: nothing to do bot at", initpos_pen, "trying to reach", position_pen)
            #
            #  already reached position
            #
            return 0
        count = 0
        total_distance_pen = 0
        if debugBulk:
            print ("ssBulNav: bot at", initpos_pen, "trying to reach", position_pen)
        me_2d = initpos_pen
        pos_2d = position_pen
        position_doom = self.p2dv (position_pen)
        #
        #  a fairly coarse grained turn, but it accurately represents our navigation
        #
        self.turnface (subVec (initpos_doom, position_doom))   # must use doom3 units for direction
        self.select (["turn"])
        if debugBulk:
            print ("completed turn along", subVec (pos_2d, me_2d))
        self.reset ()
        if debugBulk:
            print ("initpos_pen, position_pen=", initpos_pen, position_pen)
        diff_pen = absVec (subVec (position_pen, initpos_pen))
        diff_doom = absVec (subVec (position_doom, [initpos_doom[0], initpos_doom[1]]))
        distance_pen = sqrt (sqr (diff_pen[0]) + sqr (diff_pen[1]))
        distance_doom = sqrt (sqr (diff_doom[0]) + sqr (diff_doom[1])) * diagonal_scaling
        self.forward (velocity, distance_doom)
        self.select (["move"])
        if debugBulk:
            print ("completed forward", distance_pen, "units")
        self.reset ()
        mypos_pen = self.d2pv (self.getpos (self.me ()))
        if equVec (initpos_pen, mypos_pen):
            if debugBulk:
                print ("not moved substantially")
            return 0
        total_distance_pen += distance_pen
        if debugBulk:
            if equVec (position_pen, mypos_pen):
                print ("bot has reached", position_pen, "!!")
        return total_distance_pen


    #
    #
    #

    def calcDistance (self, doom3_diff, current_pen, destination_pen):
        if debugBulk:
            print ("calculate distance from", current_pen, "to", destination_pen, "doom3 distance of", doom3_diff)
        if (current_pen[0] == destination_pen[0]) or (current_pen[1] == destination_pen[1]):
            #  horizontal/vertical movement
            distance = sqrt (sqr (doom3_diff[0]) + sqr (doom3_diff[1])) * vertical_horizontal_scaling
            if debugBulk:
                print ("    horiz/vert result", distance)
        else:
            distance = sqrt (sqr (doom3_diff[0]) + sqr (doom3_diff[1])) * diagonal_scaling
            if debugBulk:
                print ("    diagonal result", distance)
        return int (distance)

    #
    #  p2dv - penguin tower vector to doom3 vector (2D).
    #

    def p2dv (self, vec_pen):
        assert (len (vec_pen) >= 2)
        doom = [vec_pen[0] * self._scaleX + self._offsetX,
                vec_pen[1] * self._scaleY + self._offsetY]
        if not equVec (vec_pen, self.d2pv (doom)):
            print ("   doom =", doom)
            print ("   self._scale2DX =", self._scale2DX, "self._scale2DY =", self._scale2DY)
            print ("   self._scaleX =", self._scaleX, "self._offsetX =", self._offsetX)
            print ("   self._scaleY =", self._scaleY, "self._offsetY =", self._offsetY)
            print ("p2dv assertion is about to fail", vec_pen, "!=", self.d2pv (doom))
        assert (equVec (vec_pen, self.d2pv (doom)))
        return doom

    #
    #  face - turn to face object, i.  If we are close we attempt to aim
    #         at object.
    #

    def face (self, i):
        self.face_position (self.getpos (i))
        self.aim (i)

    #
    #  aim - aim at object, i.
    #

    def aim (self, i):
        self._cache.reset ()
        self._cache.aim (i)

    #
    #  reset - reset the cache.
    #

    def reset (self):
        self._cache.reset ()

    #
    #  isvisible - is object i visible?
    #

    def isvisible (self, i):
        return self._cache.isvisible (i)

    #
    #  changeWeapon - change to, weapon_number.
    #                 Attempt to change to weapon_number
    #                 which is a number 0..maxweapon
    #                 The return value is the amount
    #                 of ammo left for the weapon
    #                 >= 0 if the weapon exists
    #                 or -1 if the weapon is not in
    #                 the bots inventory.
    #

    def changeWeapon (self, weapon_number):
        return self._cache.changeWeapon (weapon_number)


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
    #  startFiring - fire weapon
    #                It returns the amount of ammo left.
    #

    def startFiring (self):
        return self._cache.startFiring ()

    #
    #  stopFiring - stop firing weapon
    #                It returns the amount of ammo left.
    #

    def stopFiring (self):
        return self._cache.stopFiring ()

    #
    #  reloadWeapon - reload the current weapon
    #                 It returns the amount of ammo left.
    #

    def reloadWeapon (self):
        return self._cache.reloadWeapon ()

    #
    #  changeWeapon - change to, weapon_number.
    #                 Attempt to change to weapon_number
    #                 which is a number 0..maxweapon
    #                 The return value is the amount
    #                 of ammo left for the weapon
    #                 >= 0 if the weapon exists
    #                 or -1 if the weapon is not in
    #                 the bots inventory.
    #

    def changeWeapon (self, weapon_number):
        return self._cache.changeWeapon (weapon_number)

    #
    #  ammo - returns the amount of ammo for the weapon_number.
    #

    def ammo (self, weapon_number):
        return self._cache.ammo (weapon_number)

    #
    #  turn the visibility shader on/off.  value is a boolean.
    #

    def visibilityFlag (self, value):
        return self._cache.visibilityFlag (value)

    #
    #  visibility - assign the alpha value to tbe visibility shader.
    #               a value between 0.0 and 1.0 detemines whether
    #               the object is transparent 0.0 to non transparent 1.0.
    #

    def visibility (self, red, green = None, blue = None, alpha = None):
        if green is None:
            green = red
        if blue is None:
            blue = green
        if alpha is None:
            alpha = blue
        return self._cache.visibility (red, green, blue, alpha)

    #
    #  visibilityParams - parameters is a list of time segment durations.
    #

    def visibilityParams (self, parameters):
        return self._cache.visibilityParams (parameters)

    #
    #  flipVisibility - flip the visibility shader buffer.
    #

    def flipVisibility (self):
        return self._cache.flipVisibility ()

    #
    #  getselfentitynames - returns a list of names associated with the bot.
    #

    def getselfentitynames (self):
        return self._cache.getselfentitynames ()

    #
    #  setvisibilityshader - allows the bot to change its visibility shader.
    #                        It can change the visibility shader of different entities
    #                        which it owns.  For example weapon, head, body can be given
    #                        different shaders if required.
    #

    def setvisibilityshader (self, shader, entitylist = []):
        return self._cache.setvisibilityshader (shader, entitylist)


    #  --fixme-- implement these
    #
    #  init_bbox - create a bounded box and return its id.
    #              bbox_origin is the bottom left hand corner in the doom3 universe.
    #              bbox_size is the size of the bounded box in doom3 units.
    #

    def init_bbox (self, bbox_origin, bbox_size):
        return self._cache.init_bbox (bbox_origin, bbox_size)

    #
    #  init_bbox_entity - create a bounded box and return its id.
    #                     bbox_origin is based on the entity_num.
    #                     bbox_size is the size of the bounded box in doom3 units.
    #

    def init_bbox_entity (self, entity_num, bbox_size):
        return self._cache.init_bbox_entity (entity_num, bbox_size)

    #
    #  delete_bbox - destroy the bbox_id.
    #

    def delete_bbox (self, bbox_id):
        return self._cache.delete_bbox (bbox_id)

    #
    #  delete_bbox_all - destroy all bboxes for this bot on the doom3 server.
    #

    def delete_bbox_all (self):
        self._cache.delete_bbox_all ()

    #
    #  get_player_bbox_size - returns the bounding box size for a player
    #                         2ft x 2ft x 6ft
    #

    def get_player_bbox_size (self):
        return [2*12, 2*12, 6*12]   # x, y, z in inches

    #
    #  get_weapon_bbox_size - returns the bounding box size for a weapon
    #                         1ft x 1ft x 1ft
    #

    def get_weapon_bbox_size (self):
        return [1*12, 1*12, 1*12]   # 1 ft cube

    #
    #  get_label_bbox_size - returns the bounding box size for a weapon
    #                        1ft x 1ft x 1ft
    #

    def get_label_bbox_size (self):
        return [1*12, 1*12, 1*12]   # 1 ft cube

    #
    #  get_pen_square_bbox_size - returns the bounding box size for a weapon
    #                             4ft x 4ft x 1ft
    #

    def get_pen_square_bbox_size (self):
        return [4*12, 4*12, 1*12]   # 4ft x 4ft x 1 ft cuboid

    #
    #  get_pen_square_bbox_size - returns the bounding box size for a weapon
    #                             4ft x 4ft x 1ft
    #

    def get_pen_square_bbox_size (self):
        return [4*12, 4*12, 1*12]   # 4ft x 4ft x 1 ft cuboid


    #
    #  bbox_include_collision - enable the collision attribute of a bbox_list and
    #                           returns true if successful.
    #                           bbox_list can be "all" or ["all"] which includes all
    #                           boxes visibility attributes.
    #

    def bbox_include_collision (self, bbox_list):
        return self._cache.bbox_include_collision (bbox_list)

    #
    # bbox_exclude_collision -  disable the collision attribute of a bbox_list and
    #                           return the bbox_list if successful.
    #                           bbox_list can be "all" or ["all"] which excludes all
    #                           boxes collision attributes.
    #

    def bbox_exclude_collision (self, bbox_list):
        return self._cache.bbox_exclude_collision (bbox_list)

    #
    #  bbox_include_visibility - enable the visibility attribute bbox_list and
    #                            returns true if successful.
    #                            bbox_list can be "all" or ["all"] which includes all
    #                            boxes visibility attributes.
    #

    def bbox_enable_visibility (self, bbox_list):
        return self._cache.bbox_enable_visibilty (bbox_list)

    #
    #  bbox_exclude_visibility - disable the visibility attribute of a bbox_list and
    #                            return the bbox_list if successful.
    #                            bbox_list can be "all" or ["all"] which excludes all
    #                            boxes visibility attributes.
    #

    def bbox_exclude_visibility (self, bbox_list):
        return self._cache.bbox_exclude_visibility (bbox_list)


    #
    #  bbox_get_origin - return the doom3 units origin for the bbox.
    #                    If the offset can be specified using modifiers:
    #                    ".mid".
    #
    #  not implemented yet [".top" | ".bot" ] [ ".front" | ".back" ] [ ".left" | "right" ]
    #

    def bbox_get_origin (self, offset = None):
        return self._cache.bbox_get_origin (offset)

    #
    #  bbox_get_size - return the doom3 units size for the bbox.
    #

    def bbox_get_size (self):
        return self._cache.bbox_get_size ()

    #
    #  aim_position - bot is instructed to aim at 3d doom3 position_doom.
    #  --fixme-- implement this

    def aim_position (self, position_doom):
        return self._cache.aim_position (position_doom)

    #
    #  face_position_2d - turn and face the position_doom ignoring the Z axis.
    #                     This function will block until the bot has turned.
    #

    def face_position_2d (self, position_doom):
        self.reset ()
        me_2d = self.getpos (self.me ())[:2]
        pos_2d = position_doom[:2]
        if debugging:
            print ("face_position: ", me_2d, pos_2d)
        self.turnface (subVec (me_2d, pos_2d))
        self.select (["turn"])
        self.sync ()

    #
    #  face_position - turn and face the position_doom.
    #                  This function does not block.
    #  --fixme-- check changes to face_position_2d

    def face_position (self, position_doom, velocity = None):
        self.reset ()
        me_2d = self.getpos (self.me ())[:2]
        pos_2d = position_doom[:2]
        if debugging:
            print ("face_position: ", me_2d, pos_2d)
        self.turnface (subVec (me_2d, pos_2d), velocity)

    #  --fixme-- implement this

    def bbox_face (self, offset):
        pass

    #
    #  bbox_track - track bbox_id for ticks.  Return
    #               -1 if the bbox_id cannot be tracked,
    #               -1 indicates that the bbox_id is no
    #               longer visible.
    #               The bbox_track does not block.

    def bbox_track (self, bbox_id, ticks):
        return self._cache.bbox_track (bbox_id, ticks)

    #
    #  track - track entity_num for ticks.  Return
    #          -1 if the entity_num cannot be tracked,
    #          -1 indicates that the entity_num is no
    #          longer visible.
    #          track does not block.

    def track (self, entity_num, ticks):
        return self._cache.track (entity_num, ticks)

    def face_label (self, label_name):
        label_ent = self.label_entity (label_name)
        label_pos = self._cache.getEntityPos (label_ent)
        self.face_position (label_pos)
        self.aim (label_ent)

    def label_position (self, label_name):
        label_ent = self.label_entity (label_name)
        return self._cache.getEntityPos (label_ent)

    def label_entity (self, label_name):
        return self._cache.getEntityNo ("label", label_name)

    #
    #  footsteps - should the bot place footsteps on the floor?
    #

    def footsteps (self, on):
        return self._cache.footsteps (on)

    #
    #  footstep_base - the basename of the material entry used
    #                  for the footprint.  For example
    #                  "textures/quake1/footprint_" which will have "left"
    #                  and "right" appended to the basename.
    #                  It sets the footstep basename and returns True if the
    #                  "left" and "right" were found in the doom3
    #                  base directory.
    #

    def footstep_base (self, basename):
        return self._cache.footstep_base (basename)
