#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie! Next - New Super Mario Bros. U Level Editor
# Version v0.6
# Copyright (C) 2009-2016 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop

# This file is part of Reggie! Next.

# Reggie! is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Reggie! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Reggie!.  If not, see <http://www.gnu.org/licenses/>.



# sprites.py
# Contains code to render NSMBU sprite images
# not even close to done...need to do quite a few


################################################################
################################################################

# Imports

from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt


import spritelib as SLib
ImageCache = SLib.ImageCache


################################################################
################################################################

# GETTING SPRITEDATA:
# You can get the spritedata that is set on a sprite to alter
# the image that is shown. To do this, add a datachanged method,
# with the parameter self. In this method, you can access the
# spritedata through self.parent.spritedata[n], which returns
# the (n+1)th byte of the spritedata. To find the n for nybble
# x, use this formula:
# n = (x/2) - 1
#
# If the nybble you want is the upper 4 bits of n (odd), you
# can get the value of x like this:
# val_x = n >> 4
#
# A BIT EASIER TO UNDERSTAND
# Every 2 nybbles is a X value for
# self.parent.spritedata[X]
# so for example: 0000 0000 0001 0000 0000 0000 -- If you wanted to get just that one value, you'd do
# self.parent.spritedata[5] & 1 -- because the value by itself would effect nybble 11 AND 12, causing 0011 to break

class SpriteImage_Block(SLib.SpriteImage):
    def __init__(self, parent, scale=1.5):
        super().__init__(parent, scale)
        self.spritebox.shown = False
        self.contentsOverride = None

        self.tilenum = 1315
        self.tileheight = 1
        self.tilewidth = 1
        # Make this negative to move this up a block, positive to move down.
        # 12 is an entire block move, so 6 is a half-block move.
        self.yOffset = 0
        self.xOffset = 0
        self.invisiblock = False

    def dataChanged(self):
        super().dataChanged()

        if self.contentsOverride is not None:
            self.image = ImageCache['Items'][self.contentsOverride]
        else:
            self.contents = self.parent.spritedata[9] & 0xF
            self.acorn = (self.parent.spritedata[6] >> 4) & 1

            if self.acorn:
                self.image = ImageCache['Items'][15]
            elif self.contents != 0:
                self.image = ImageCache['Items'][self.contents-1]
            else:
                self.image = None

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.tilenum < len(SLib.Tiles):
            if self.invisiblock:
                painter.drawPixmap(0, 0, ImageCache['InvisiBlock'])
            else:
                painter.drawPixmap(self.yOffset, self.xOffset, self.tilewidth*60, self.tileheight*60, SLib.Tiles[self.tilenum].main)
        if self.image is not None:
            painter.drawPixmap(0, 0, self.image)

class SpriteImage_Pipe(SLib.SpriteImage):
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.spritebox.shown = self.mini = False
        self.hasTop = True
        self.direction = 'U'
        self.colours = ("Green", "Red", "Yellow", "Blue")
        self.topY = self.topX = self.colour = self.extraLength = self.x = self.y = 0
        self.width = self.height = 32
        self.pipeHeight = self.pipeWidth = 120
        self.parent.setZValue(24999)

    @staticmethod
    def loadImages():
        if 'PipeTopGreen' not in ImageCache:
            for colour in ("Green", "Red", "Yellow", "Blue"):
                ImageCache['PipeTop%s' % colour] = SLib.GetImg('pipe_%s_top.png' % colour.lower())
                ImageCache['PipeMiddleV%s' % colour] = SLib.GetImg('pipe_%s_middleV.png' % colour.lower())
                ImageCache['PipeMiddleH%s' % colour] = SLib.GetImg('pipe_%s_middleH.png' % colour.lower())
                ImageCache['PipeBottom%s' % colour] = SLib.GetImg('pipe_%s_bottom.png' % colour.lower())
                ImageCache['PipeLeft%s' % colour] = SLib.GetImg('pipe_%s_left.png' % colour.lower())
                ImageCache['PipeRight%s' % colour] = SLib.GetImg('pipe_%s_right.png' % colour.lower())
                if colour == "Green":
                    ImageCache['MiniPipeTop%s' % colour] = SLib.GetImg('pipe_mini_%s_top.png' % colour.lower())
                    ImageCache['MiniPipeMiddleV%s' % colour] = SLib.GetImg('pipe_mini_%s_middleV.png' % colour.lower())
                    ImageCache['MiniPipeMiddleH%s' % colour] = SLib.GetImg('pipe_mini_%s_middleH.png' % colour.lower())
                    ImageCache['MiniPipeBottom%s' % colour] = SLib.GetImg('pipe_mini_%s_bottom.png' % colour.lower())
                    ImageCache['MiniPipeLeft%s' % colour] = SLib.GetImg('pipe_mini_%s_left.png' % colour.lower())
                    ImageCache['MiniPipeRight%s' % colour] = SLib.GetImg('pipe_mini_%s_right.png' % colour.lower())

    def dataChanged(self):
        super().dataChanged()
        rawlength = (self.parent.spritedata[5] & 0x0F) + 1
        if not self.mini:
            rawtop = self.parent.spritedata[2] >> 4
            rawcolour = self.parent.spritedata[5] >> 4

            if rawtop == 1:
                pipeLength = rawlength + self.extraLength + 1
            else:
                pipeLength = rawlength + self.extraLength

            if rawcolour > 12:
                rawcolour -= 13
            elif rawcolour > 9:
                rawcolour -= 10
            elif rawcolour > 6:
                rawcolour -= 7
            elif rawcolour > 3:
                rawcolour -= 4
            self.colour = self.colours[rawcolour]
        else:
            pipeLength = rawlength
            self.colour = "Green"

        if self.direction in 'LR': # horizontal
            self.pipeWidth = pipeLength * 60
            self.width = (self.pipeWidth/3.75)
            if not self.mini:
                self.middle = ImageCache['PipeMiddleH%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleH%s' % self.colour]
                self.height = 16
                self.pipeHeight = 60

            if self.direction == 'R': # faces right
                if not self.mini:
                    self.top = ImageCache['PipeRight%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeRight%s' % self.colour]
                self.topX = self.pipeWidth - 60
            else: # faces left
                if not self.mini:
                    self.top = ImageCache['PipeLeft%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeLeft%s' % self.colour]
                self.xOffset = 16 - self.width

        if self.direction in 'UD': # vertical
            self.pipeHeight = pipeLength * 60
            self.height = (self.pipeHeight/3.75)
            if not self.mini:
                self.middle = ImageCache['PipeMiddleV%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleV%s' % self.colour]
                self.width = 16
                self.pipeWidth = 60

            if self.direction == 'D': # faces down
                if not self.mini:
                    self.top = ImageCache['PipeBottom%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeBottom%s' % self.colour]
                self.topY = self.pipeHeight - 60
            else: # faces up
                if not self.mini:
                    self.top = ImageCache['PipeTop%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeTop%s' % self.colour]
                self.yOffset = 16 - (self.pipeHeight/3.75)

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)

class SpriteImage_Goomba(SLib.SpriteImage_Static): # 0
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Goomba'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Goomba', 'goomba.png')

class SpriteImage_Paragoomba(SLib.SpriteImage_Static): # 1
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Paragoomba'],
            (-8, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Paragoomba', 'paragoomba.png')
  
# Image needs to be improved
class SpriteImage_KoopaTroopa(SLib.SpriteImage_StaticMultiple): # 19
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['KoopaG'],
            (-8,-8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaG', 'koopa_green.png')
        SLib.loadIfNotInImageCache('KoopaR', 'koopa_red.png')

    def dataChanged(self):
        shellcolour = self.parent.spritedata[5] & 1

        if shellcolour == 0:
            self.image = ImageCache['KoopaG']
        else:
            self.image = ImageCache['KoopaR']
            
        super().dataChanged()

class SpriteImage_Spiny(SLib.SpriteImage_StaticMultiple): # 23
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        
        self.yOffset = -1

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spiny', 'spiny_norm.png')
        SLib.loadIfNotInImageCache('SpinyBall', 'spiny_ball.png')
        SLib.loadIfNotInImageCache('SpinyShell', 'spiny_shell.png')
        SLib.loadIfNotInImageCache('SpinyShellU', 'spiny_shell_u.png')

    def dataChanged(self):          
        
        spawntype = self.parent.spritedata[5]
        
        if spawntype == 0:
            self.image = ImageCache['Spiny']
        elif spawntype == 1:
            self.image = ImageCache['SpinyBall']
        elif spawntype == 2:
            self.image = ImageCache['SpinyShell']
        elif spawntype == 3:
            self.image = ImageCache['SpinyShellU']
        else:
            self.image = ImageCache['Spiny']
            
        super().dataChanged()

class SpriteImage_MidwayFlag(SLib.SpriteImage_StaticMultiple): # 25
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MidwayFlag'],
            )
        
        self.yOffset = -41

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MidwayFlag', 'midway_flag.png')


class SpriteImage_ArrowSignboard(SLib.SpriteImage_StaticMultiple): # 32
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ArrowSign0'],
            (-7,-14),
            )

    @staticmethod
    def loadImages():
        for i in range(0,8):
            for j in ('', 's'):
                SLib.loadIfNotInImageCache('ArrowSign{0}{1}'.format(i, j), 'sign{0}{1}.png'.format(i, j))

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF
        if direction > 7: direction -= 8
        appear_raw = self.parent.spritedata[3] >> 4
        appear = ''
        if appear_raw == 1:
            appear = 's'

        self.image = ImageCache['ArrowSign{0}{1}'.format(direction, appear)]

        super().dataChanged()

class SpriteImage_RedRing(SLib.SpriteImage_Static): # 44
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RedRing'],
            )
        
        self.yOffset = -14
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RedRing', 'red_ring.png')  

class SpriteImage_GreenCoin(SLib.SpriteImage_Static): # 50
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GreenCoin'],
            )
        
        self.xOffset = -7
        self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GreenCoin', 'green_coins.png')  

class SpriteImage_QBlock(SpriteImage_Block): # 59
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.tilenum = 49

class SpriteImage_BrickBlock(SpriteImage_Block): # 60
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.tilenum = 48

class SpriteImage_InvisiBlock(SpriteImage_Block): # 61
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.invisiblock = True

class SpriteImage_StalkingPiranha(SLib.SpriteImage_StaticMultiple): # 63
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StalkingPiranha'],
            )
        
        self.yOffset = -17
        #self.xOffset = -10

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StalkingPiranha', 'stalking_piranha.png')    

class SpriteImage_Coin(SLib.SpriteImage_Static): # 65
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)


class SpriteImage_HuckitCrab(SLib.SpriteImage_StaticMultiple): # 74
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['HuckitCrab'],
            )
        
        self.yOffset = -4.5 # close enough, it can't be a whole number
        self.xOffset = -10

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HuckitCrab', 'huckit_crab.png')          

class SpriteImage_MovingCoin(SLib.SpriteImage_Static): # 87
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_QuestionSwitch(SLib.SpriteImage_Static): # 104
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['QSwitch'],
            )

    @staticmethod
    def loadImages():
        if 'QSwitch' not in ImageCache:
            # we need to cache 2 things, the regular switch, and the upside down one
            image = SLib.GetImg('q_switch.png', True)
            # now we set up a transform to turn the switch upside down
            transform180 = QtGui.QTransform()
            transform180.rotate(180)
            # now we store it
            ImageCache['QSwitch'] = QtGui.QPixmap.fromImage(image)
            ImageCache['QSwitchU'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
        
    def dataChanged(self):
        isflipped = self.parent.spritedata[5] & 1

        if isflipped == 0:
            self.image = ImageCache['QSwitch']
        else:
            self.image = ImageCache['QSwitchU']
            
        super().dataChanged()
                  

class SpriteImage_PSwitch(SLib.SpriteImage_Static): # 105
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PSwitch'],
            )

    @staticmethod
    def loadImages():
        if 'PSwitch' not in ImageCache:
            # we need to cache 2 things, the regular switch, and the upside down one
            image = SLib.GetImg('p_switch.png', True)
            # now we set up a transform to turn the switch upside down
            transform180 = QtGui.QTransform()
            transform180.rotate(180)        
            # now we store it
            ImageCache['PSwitch'] = QtGui.QPixmap.fromImage(image)
            ImageCache['PSwitchU'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
        
    def dataChanged(self):
        isflipped = self.parent.spritedata[5] & 1

        if isflipped == 0:
            self.image = ImageCache['PSwitch']
        else:
            self.image = ImageCache['PSwitchU']
            
        super().dataChanged()

class SpriteImage_SandPillar(SLib.SpriteImage_Static): # 123
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SandPillar'],
            )

        self.yOffset = -143 # what
        self.xOffset = -18

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SandPillar', 'sand_pillar.png')

class SpriteImage_DryBones(SLib.SpriteImage_StaticMultiple): # 137
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['DryBones'],
            )
        
        self.yOffset = -12
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DryBones', 'dry_bones.png')  
                  

class SpriteImage_BigDryBones(SLib.SpriteImage_StaticMultiple): # 138
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigDryBones'],
            )
        
        self.yOffset = -21
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigDryBones', 'big_dry_bones.png')
        
class SpriteImage_PipeUp(SpriteImage_Pipe): # 139
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'

class SpriteImage_PipeDown(SpriteImage_Pipe): # 140
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'D'

class SpriteImage_PipeLeft(SpriteImage_Pipe): # 141
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'L'

class SpriteImage_PipeRight(SpriteImage_Pipe): # 142
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'R'

class SpriteImage_BubbleYoshi(SLib.SpriteImage_Static): # 143, 243
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BubbleYoshi'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BubbleYoshi', 'babyyoshibubble.png')
       
class SpriteImage_POWBlock(SLib.SpriteImage_Static): # 152
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['POWBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('POWBlock', 'block_pow.png')  

class SpriteImage_CoinOutline(SLib.SpriteImage_StaticMultiple): # 158
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75, # native res (3.75*16=60)
            ImageCache['CoinOutlineMultiplayer'],
            )
        self.parent.setZValue(20000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CoinOutline', 'coin_outline.png')
        SLib.loadIfNotInImageCache('CoinOutlineMultiplayer', 'coin_outline_multiplayer.png')

    def dataChanged(self):
        multi = (self.parent.spritedata[2] >> 4) & 1
        self.image = ImageCache['CoinOutline' + ('Multiplayer' if multi else '')]
        super().dataChanged()

class SpriteImage_Parabomb(SLib.SpriteImage_StaticMultiple): # 170
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabomb'],
            )
        
        self.yOffset = -16
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabomb', 'parabomb.png')          

class SpriteImage_Mechakoopa(SLib.SpriteImage_StaticMultiple): # 175
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Mechakoopa'],
            )
        
        self.yOffset = -10
        self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Mechakoopa', 'mechakoopa.png')        

class SpriteImage_AirshipCannon(SLib.SpriteImage_StaticMultiple): # 176
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

        self.yOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CannonL', 'Cannon_L.png')
        SLib.loadIfNotInImageCache('CannonR', 'Cannon_R.png')

    def dataChanged(self):          
        
        direction = self.parent.spritedata[5]
        
        if direction == 0:
            self.image = ImageCache['CannonL']
        elif direction == 1:
            self.image = ImageCache['CannonR']
        else:
            self.image = ImageCache['CannonL']
            
        super().dataChanged()

class SpriteImage_FallingIcicle(SLib.SpriteImage_StaticMultiple): # 183
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FallingIcicle1x1', 'falling_icicle_1x1.png')
        SLib.loadIfNotInImageCache('FallingIcicle1x2', 'falling_icicle_1x2.png')

    def dataChanged(self):          
        
        size = self.parent.spritedata[5]
        
        if size == 0:
            self.image = ImageCache['FallingIcicle1x1']
        elif size == 1:
            self.image = ImageCache['FallingIcicle1x2']
        else:
            self.image = ImageCache['FallingIcicle1x1']
            
        super().dataChanged()

class SpriteImage_GiantIcicle(SLib.SpriteImage_Static): # 184
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GiantIcicle'],
            )
        
        self.xOffset = -24

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantIcicle', 'giant_icicle.png')    

class SpriteImage_RouletteBlock(SLib.SpriteImage_StaticMultiple): # 195
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RouletteBlock'],
            )
        
        #self.yOffset = -17
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RouletteBlock', 'block_roulette.png')        

class SpriteImage_Springboard(SLib.SpriteImage_Static): # 215
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Springboard'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Springboard', 'springboard.png')         

class SpriteImage_BalloonYoshi(SLib.SpriteImage_Static): # 224
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BalloonYoshi'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BalloonYoshi', 'balloonbabyyoshi.png')

class SpriteImage_TileGod(SLib.SpriteImage): # 237
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        width = self.parent.spritedata[8] & 0xF
        height = self.parent.spritedata[5] >> 4
        if width == 0: width = 1
        if height == 0: height = 1
        if width == 1 and height == 1:
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(width * 60, height * 60)

class SpriteImage_Bolt(SLib.SpriteImage_StaticMultiple): # 238
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

        self.yOffset = 3

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltMetal', 'bolt_metal.png')
        SLib.loadIfNotInImageCache('BoltStone', 'bolt_stone.png')

    def dataChanged(self):
        stone = self.parent.spritedata[4] & 1

        if stone == 1:
            self.image = ImageCache['BoltStone']
        else:
            self.image = ImageCache['BoltMetal']
            
        super().dataChanged()    

class SpriteImage_PricklyGoomba(SLib.SpriteImage_StaticMultiple): # 247
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PricklyGoomba'],
            )
        
        self.yOffset = -13
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PricklyGoomba', 'prickly_goomba.png')           

class SpriteImage_Wiggler(SLib.SpriteImage_StaticMultiple): # 249
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Wiggler'],
            )
        
        self.yOffset = -17
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wiggler', 'wiggler.png')         

class SpriteImage_Muncher(SLib.SpriteImage_StaticMultiple): # 259
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ) 

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MuncherReg', 'muncher.png')
        SLib.loadIfNotInImageCache('MuncherFr', 'muncher_frozen.png')

    def dataChanged(self):
        isfrozen = self.parent.spritedata[5] & 1

        if isfrozen == 0:
            self.image = ImageCache['MuncherReg']
        else:
            self.image = ImageCache['MuncherFr']
            
        super().dataChanged()        

class SpriteImage_Parabeetle(SLib.SpriteImage_Static): # 261
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabeetle'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabeetle', 'parabeetle.png')

class SpriteImage_NoteBlock(SLib.SpriteImage_Static): # 295
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NoteBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NoteBlock', 'noteblock.png')

class SpriteImage_Broozer(SLib.SpriteImage_Static): # 320
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Broozer'],
            )

        self.xOffset = -20
        self.yOffset = -20

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Broozer', 'broozer.png')

class SpriteImage_Barrel(SLib.SpriteImage_Static): # 323 -- BARRELS
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Barrel'],
            )
        
        self.xOffset = -7
        self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Barrel', 'barrel.png')

class SpriteImage_RotationControlledCoin(SLib.SpriteImage_Static): # 325
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_MovementControlledCoin(SLib.SpriteImage_Static): # 326
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_BoltControlledCoin(SLib.SpriteImage_Static): # 328
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_Cooligan(SLib.SpriteImage_StaticMultiple): # 334
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        
        self.xOffset = -7
        self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CooliganL', 'cooligan_l.png')
        SLib.loadIfNotInImageCache('CooliganR', 'cooligan_r.png')

    def dataChanged(self):
        
        direction = self.parent.spritedata[5]

        if direction == 0:
            self.image = ImageCache['CooliganL']
        elif direction == 1:
            self.image = ImageCache['CooliganR']
        elif direction == 2:
            self.image = ImageCache['CooliganL']
        else:
            self.image = ImageCache['CooliganL']

        super().dataChanged()

class SpriteImage_Bramball(SLib.SpriteImage_Static): # 336
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Bramball'],
            )
        
        self.xOffset = -30
        self.yOffset = -46

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bramball', 'bramball.png')    


class SpriteImage_WoodenBox(SLib.SpriteImage_StaticMultiple): # 338
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Reg2x2', 'reg_box_2x2.png')
        SLib.loadIfNotInImageCache('Reg4x2', 'reg_box_4x2.png')
        SLib.loadIfNotInImageCache('Reg2x4', 'reg_box_2x4.png')
        SLib.loadIfNotInImageCache('Reg4x4', 'reg_box_4x4.png')                
        SLib.loadIfNotInImageCache('Inv2x2', 'inv_box_2x2.png')
        SLib.loadIfNotInImageCache('Inv4x2', 'inv_box_4x2.png')
        SLib.loadIfNotInImageCache('Inv2x4', 'inv_box_2x4.png')
        SLib.loadIfNotInImageCache('Inv4x4', 'inv_box_4x4.png')        

    def dataChanged(self):          
        
        boxcolor = self.parent.spritedata[4]
        boxsize = self.parent.spritedata[5] >> 4
        
        if boxsize == 0 and boxcolor == 0:
            self.image = ImageCache['Reg2x2']
        elif boxsize == 1 and boxcolor == 0:
            self.image = ImageCache['Reg2x4']
        elif boxsize == 2 and boxcolor == 0:
            self.image = ImageCache['Reg4x2']
        elif boxsize == 3 and boxcolor == 0:
            self.image = ImageCache['Reg4x4']
        elif boxsize == 0 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv2x2']
        elif boxsize == 1 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv2x4']
        elif boxsize == 2 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv4x2']
        elif boxsize == 3 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv4x4']
        else:
            self.image = ImageCache['Reg2x2'] # let's not make some nonsense out of this
            
        super().dataChanged()
   
class SpriteImage_SuperGuide(SLib.SpriteImage_Static): # 348
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SuperGuide'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SuperGuide', 'guide_block.png')          

class SpriteImage_GoldenYoshi(SLib.SpriteImage_Static): # 365
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GoldenYoshi'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GoldenYoshi', 'babyyoshiglowing.png')

class SpriteImage_TorpedoLauncher(SLib.SpriteImage_StaticMultiple): # 378
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['TorpedoLauncher'],
            )
        
        #self.yOffset = -17
        self.xOffset = -22

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TorpedoLauncher', 'torpedo_launcher.png')  

class SpriteImage_GreenRing(SLib.SpriteImage_Static): # 402
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GreenRing'],
            )
        
        self.yOffset = -14
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GreenRing', 'green_ring.png')  

class SpriteImage_PipeUpEnterable(SpriteImage_Pipe): # 404
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'
        self.extraHeight = 1

class SpriteImage_BumpPlatform(SLib.SpriteImage): # 407
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.spritebox.shown = False
        
    @staticmethod
    def loadImages():
        ImageCache['BumpPlatformL'] = SLib.GetImg('bump_platform_l.png')
        ImageCache['BumpPlatformM'] = SLib.GetImg('bump_platform_m.png')
        ImageCache['BumpPlatformR'] = SLib.GetImg('bump_platform_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = ((self.parent.spritedata[8] & 0xF) + 1) << 4

    def paint(self, painter):
        super().paint(painter)
        
        if self.width > 32:
            painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['BumpPlatformM'])

        if self.width == 24:
            painter.drawPixmap(0, 0, ImageCache['BumpPlatformR'])
            painter.drawPixmap(8, 0, ImageCache['BumpPlatformL'])
        else:
            # normal rendering
            painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['BumpPlatformR'])
            painter.drawPixmap(0, 0, ImageCache['BumpPlatformL'])

class SpriteImage_BigBrickBlock(SLib.SpriteImage_Static): # 422
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigBrick'],
            )
        
        self.yOffset = 16

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigBrick', 'big_brickblock.png')

class SpriteImage_Fliprus(SLib.SpriteImage_StaticMultiple): # 441
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        
        self.yOffset = -16
        self.xOffset = -6

    @staticmethod
    def loadImages():
        if "FliprusL" not in ImageCache:
            fliprus = SLib.GetImg('fliprus.png', True)
            ImageCache['FliprusL'] = QtGui.QPixmap.fromImage(fliprus)
            ImageCache['FliprusR'] = QtGui.QPixmap.fromImage(fliprus.mirrored(True, False))

    def dataChanged(self):
        direction = self.parent.spritedata[4]

        if direction == 0:
            self.image = ImageCache['FliprusL']
        elif direction == 1:
            self.image = ImageCache['FliprusR']
        elif direction == 2:
            self.image = ImageCache['FliprusL']
        else:
            self.image = ImageCache['FliprusL']
            
        super().dataChanged()        
        

class SpriteImage_BonyBeetle(SLib.SpriteImage_Static): # 443
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BonyBeetle'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BonyBeetle', 'bony_beetle.png')

class SpriteImage_FliprusSnowball(SLib.SpriteImage_StaticMultiple): # 446
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Snowball'],
            )
        
        self.yOffset = -10
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Snowball', 'snowball.png')

class SpriteImage_BigGoomba(SLib.SpriteImage_StaticMultiple): # 472
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigGoomba'],
            )
        
        self.yOffset = -20

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigGoomba', 'big_goomba.png')

class SpriteImage_BigQBlock(SLib.SpriteImage_Static): # 475
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigQBlock'],
            )

        self.yOffset = 16  

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigQBlock', 'big_qblock.png')

class SpriteImage_BigKoopaTroopa(SLib.SpriteImage_StaticMultiple): # 476
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

        self.yOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigKoopaG', 'big_koopa_green.png')
        SLib.loadIfNotInImageCache('BigKoopaR', 'big_koopa_red.png')

    def dataChanged(self):          
        
        color = self.parent.spritedata[5] & 1
        
        if color == 0:
            self.image = ImageCache['BigKoopaG']
        elif color == 1:
            self.image = ImageCache['BigKoopaR']
        else:
            self.image = ImageCache['BigKoopaG']
            
        super().dataChanged()

class SpriteImage_WaddleWing(SLib.SpriteImage_StaticMultiple): # 481
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ) #What image to load is taken care of later

        self.yOffset = -9
        self.xOffset = -9

    @staticmethod
    def loadImages():
        waddlewing = SLib.GetImg('waddlewing.png', True)

        ImageCache['WaddlewingL'] = QtGui.QPixmap.fromImage(waddlewing)
        ImageCache['WaddlewingR'] = QtGui.QPixmap.fromImage(waddlewing.mirrored(True, False))

    def dataChanged(self):
        rawdir = self.parent.spritedata[5]

        if rawdir == 2:
            self.image = ImageCache['WaddlewingR']
        else:
            self.image = ImageCache['WaddlewingL']
            
        super().dataChanged()

class SpriteImage_BoltControlledMovingCoin(SLib.SpriteImage_Static): # 496
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_MovingGrassPlatform(SLib.SpriteImage): # 499
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.parent.setZValue(24999)

    def dataChanged(self):
        super().dataChanged()

        width = (self.parent.spritedata[8] & 0xF) + 1
        height = (self.parent.spritedata[9] & 0xF) + 1
        if width == 1 and height == 1:
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(width * 60, height * 60)

class SpriteImage_Grrrol(SLib.SpriteImage_StaticMultiple): # 504
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GrrrolSmall'],
            )
        
        self.yOffset = -12
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrrrolSmall', 'grrrol_small.png')

class SpriteImage_PipeJoint(SLib.SpriteImage_Static): # 513
    def __init__(self, parent, scale=3.75):
        super().__init__(
            parent,
            scale,
            ImageCache['PipeJoint'])

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJoint', 'pipe_joint.png')

class SpriteImage_PipeJointSmall(SLib.SpriteImage_Static): # 514
    def __init__(self, parent, scale=3.75):
        super().__init__(
            parent,
            scale,
            ImageCache['PipeJointSmall'])

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJointSmall', 'pipe_joint_mini.png')

class SpriteImage_MiniPipeRight(SpriteImage_Pipe): # 516
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'R'

class SpriteImage_MiniPipeLeft(SpriteImage_Pipe): # 517
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'L'

class SpriteImage_MiniPipeUp(SpriteImage_Pipe): # 518
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'U'

class SpriteImage_MiniPipeDown(SpriteImage_Pipe): # 519
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'D'

class SpriteImage_BouncyMushroomPlatform(SLib.SpriteImage): # 542
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.spritebox.shown = False
        
    @staticmethod
    def loadImages():
        ImageCache['SkinnyOrangeL'] = SLib.GetImg('orange_mushroom_skinny_l.png')
        ImageCache['SkinnyOrangeM'] = SLib.GetImg('orange_mushroom_skinny_m.png')
        ImageCache['SkinnyOrangeR'] = SLib.GetImg('orange_mushroom_skinny_r.png')
        ImageCache['SkinnyGreenL'] = SLib.GetImg('green_mushroom_skinny_l.png')
        ImageCache['SkinnyGreenM'] = SLib.GetImg('green_mushroom_skinny_m.png')
        ImageCache['SkinnyGreenR'] = SLib.GetImg('green_mushroom_skinny_r.png')
        ImageCache['ThickBlueL'] = SLib.GetImg('blue_mushroom_thick_l.png')
        ImageCache['ThickBlueM'] = SLib.GetImg('blue_mushroom_thick_m.png')
        ImageCache['ThickBlueR'] = SLib.GetImg('blue_mushroom_thick_r.png')
        ImageCache['ThickRedL'] = SLib.GetImg('red_mushroom_thick_l.png')
        ImageCache['ThickRedM'] = SLib.GetImg('red_mushroom_thick_m.png')
        ImageCache['ThickRedR'] = SLib.GetImg('red_mushroom_thick_r.png')               


    def dataChanged(self):
        super().dataChanged()

        self.color = self.parent.spritedata[4] & 1
        self.girth = self.parent.spritedata[5] >> 4 & 1
        if self.girth == 1:
            self.width = ((self.parent.spritedata[8] & 0xF) + 3) << 4 # because default crapo
            self.height = 30
        else:
            self.width = ((self.parent.spritedata[8] & 0xF) + 2) << 4

    def paint(self, painter):
        super().paint(painter)

        # this is coded so horribly
        
        if self.width > 32:
            if self.color == 0 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyOrangeM'])
            elif self.color == 1 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyGreenM'])
            elif self.color == 0 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickRedM'])
            elif self.color == 1 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickBlueM'])                    
            else:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyOrangeM'])

        if self.width == 24:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyOrangeL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyGreenR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyGreenL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(8, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(8, 0, ImageCache['ThickBlueL'])                    
            else:
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyOrangeL'])                
        else:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyGreenR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyGreenL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(0, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(0, 0, ImageCache['ThickBlueL'])                 
            else:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeL'])                

class SpriteImage_Goombrat(SLib.SpriteImage_StaticMultiple): # 595
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Goombrat'],
            )
        
        #self.yOffset = -17
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Goombrat', 'goombrat.png')

class SpriteImage_BlueRing(SLib.SpriteImage_Static): # 662
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BlueRing'],
            )
        
        self.yOffset = -14
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BlueRing', 'blue_ring.png')  

################################################################
################################################################


ImageClasses = {
    0: SpriteImage_Goomba,
    1: SpriteImage_Paragoomba,
    19: SpriteImage_KoopaTroopa,
    23: SpriteImage_Spiny,
    25: SpriteImage_MidwayFlag,
    32: SpriteImage_ArrowSignboard,
    44: SpriteImage_RedRing,
    50: SpriteImage_GreenCoin,
    59: SpriteImage_QBlock,
    60: SpriteImage_BrickBlock,
    61: SpriteImage_InvisiBlock,
    63: SpriteImage_StalkingPiranha,
    65: SpriteImage_Coin,
    66: SpriteImage_Coin,
    74: SpriteImage_HuckitCrab,
    87: SpriteImage_MovingCoin,
    104: SpriteImage_QuestionSwitch,
    105: SpriteImage_PSwitch,
    123: SpriteImage_SandPillar,
    137: SpriteImage_DryBones,
    138: SpriteImage_BigDryBones,
    139: SpriteImage_PipeUp,
    140: SpriteImage_PipeDown,
    141: SpriteImage_PipeLeft,
    142: SpriteImage_PipeRight,
    143: SpriteImage_BubbleYoshi,
    152: SpriteImage_POWBlock,
    158: SpriteImage_CoinOutline,
    170: SpriteImage_Parabomb,
    175: SpriteImage_Mechakoopa,
    176: SpriteImage_AirshipCannon,
    183: SpriteImage_FallingIcicle,
    184: SpriteImage_GiantIcicle,
    195: SpriteImage_RouletteBlock,
    215: SpriteImage_Springboard,
    224: SpriteImage_BalloonYoshi,
    237: SpriteImage_TileGod,
    238: SpriteImage_Bolt,
    243: SpriteImage_BubbleYoshi,
    247: SpriteImage_PricklyGoomba,
    249: SpriteImage_Wiggler,
    259: SpriteImage_Muncher,
    261: SpriteImage_Parabeetle,
    295: SpriteImage_NoteBlock,
    320: SpriteImage_Broozer,
    323: SpriteImage_Barrel,
    325: SpriteImage_RotationControlledCoin,
    326: SpriteImage_MovementControlledCoin,
    328: SpriteImage_BoltControlledCoin,
    334: SpriteImage_Cooligan,
    336: SpriteImage_Bramball,
    338: SpriteImage_WoodenBox,    
    348: SpriteImage_SuperGuide,
    365: SpriteImage_GoldenYoshi,
    378: SpriteImage_TorpedoLauncher,
    402: SpriteImage_GreenRing,
    404: SpriteImage_PipeUpEnterable,
    407: SpriteImage_BumpPlatform,
    422: SpriteImage_BigBrickBlock,
    441: SpriteImage_Fliprus,
    446: SpriteImage_FliprusSnowball,
    472: SpriteImage_BigGoomba,
    475: SpriteImage_BigQBlock,
    476: SpriteImage_BigKoopaTroopa,
    481: SpriteImage_WaddleWing,
    496: SpriteImage_BoltControlledMovingCoin,
    499: SpriteImage_MovingGrassPlatform,
    504: SpriteImage_Grrrol,
    511: SpriteImage_PipeDown,
    513: SpriteImage_PipeJoint,
    514: SpriteImage_PipeJointSmall,
    516: SpriteImage_MiniPipeRight,
    517: SpriteImage_MiniPipeLeft,
    518: SpriteImage_MiniPipeUp,
    519: SpriteImage_MiniPipeDown,
    542: SpriteImage_BouncyMushroomPlatform,
    595: SpriteImage_Goombrat,
    662: SpriteImage_BlueRing,
}
