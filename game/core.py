import statistics
from collections import deque

import pygame
import time

import settings


class Engine(object):

    EVENTS_UPDATE = pygame.USEREVENT + 1
    EVENTS_RENDER = pygame.USEREVENT + 2

    def __init__(self, title, width, height, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)

        pygame.mixer.init()
        pygame.init()

        # ── Display setup ──────────────────────────────────────────────────────
        # DOUBLEBUF + HWSURFACE enables hardware double-buffering.
        # FULLSCREEN on Pi avoids X11 window manager overhead.
        # We do NOT use pygame.SCALED — it forces software scaling every frame
        # which pins the Pi Zero 2W CPU to ~100%. Render at native 480×320.
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        if settings.FULLSCREEN or settings.PI:
            flags |= pygame.FULLSCREEN
        self.window = pygame.display.set_mode((width, height), flags)
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption(title)
        pygame.mouse.set_visible(False)

        self.groups = []
        self.root_persitant = EntityGroup()
        self.background = pygame.surface.Surface(self.screen.get_size())
        self.background.fill(settings.black)
        # Convert background once so every blit uses the display pixel format
        self.background = self.background.convert()

        self.rescale = False
        self.last_render_time = 0
        self.prev_time = 0
        self.rects_to_update = []
        self.prev_fps_time = 0
        self.fps_average = deque(maxlen=8)

        # pygame.time.Clock is more accurate than manual time.time() waits
        self._clock = pygame.time.Clock()

    def render(self):
        self.current_time = time.time()
        self.delta_time = self.current_time - self.prev_time

        if self.delta_time < settings.fps_rate:
            # Nothing to do yet — yield the rest of this slice to the OS
            # so the CPU isn't spinning at 100% between frames.
            sleep_ms = int((settings.fps_rate - self.delta_time) * 1000)
            if sleep_ms > 1:
                pygame.time.wait(sleep_ms)
            return

        self.prev_time = self.current_time

        # ── Draw ───────────────────────────────────────────────────────────────
        # LayeredDirty.draw() returns a list of pygame.Rect objects for every
        # sprite that was dirty this frame. Collecting those lets us call
        # display.update(dirty_rects) instead of display.flip(), so only
        # changed screen regions are sent to the display hardware.
        dirty = self.root_persitant.draw(self.screen)
        self.root_persitant.render()
        for group in self.groups:
            group.render()
            dirty += group.draw(self.screen)

        # ── FPS overlay (top-left, green) ──────────────────────────────────────
        current_time = time.time()
        fps_delta = current_time - self.prev_fps_time
        self.prev_fps_time = current_time
        if fps_delta > 0:
            self.fps_average.append(int(1 / fps_delta))
        fps_display = int(statistics.mean(self.fps_average)) if self.fps_average else 0
        fps_rect = settings.FreeRobotoB[20].render_to(
            self.screen, (0, 0), str(fps_display), settings.bright, settings.black
        )
        dirty.append(fps_rect[1])  # include FPS text region in dirty list

        # ── Only refresh the pixels that actually changed this frame ───────────
        if dirty:
            pygame.display.update(dirty)
        # Fallback: full flip if nothing reported dirty (should not happen often)
        # else:
        #     pygame.display.flip()

        # Cap to target FPS using the pygame clock (more accurate than wait)
        self._clock.tick(settings.frame_per_second)

    def add(self, group):
        if group not in self.groups:
            self.groups.append(group)

    def remove(self, group):
        if group in self.groups:
            self.groups.remove(group)


class EntityGroup(pygame.sprite.LayeredDirty):
    """LayeredDirty tracks which sprites changed each frame, enabling
    dirty-rectangle rendering without manual rect bookkeeping."""

    def render(self):
        for entity in self:
            entity.render()

    def move(self, x, y):
        for child in self:
            child.rect.move(x, y)


class Entity(pygame.sprite.DirtySprite):
    """Base sprite. Uses DirtySprite so the group knows when to redraw it."""

    def __init__(self, dimensions=(0, 0), layer=0, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.image = pygame.surface.Surface(dimensions)
        self.rect = self.image.get_rect()
        # convert_alpha() matches the display surface pixel format; avoids
        # per-pixel format conversion on every blit.
        self.image = self.image.convert_alpha()
        self.groups_list = pygame.sprite.LayeredDirty()
        self.layer = layer
        self.dirty = 1          # 1 = draw once; 2 = always redraw (animations)
        self.blendmode = pygame.BLEND_RGB_ADD

    def render(self, *args, **kwargs):
        pass

    def __le__(self, other):
        if type(self) == type(other):
            return self.label <= other.label
        else:
            return 0

    def __str__(self):
        return "Entity"
