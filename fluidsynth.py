"""
================================================================================

    pyFluidSynth

    Python bindings for FluidSynth

    Copyright 2008-2019, Nathan Whitehead <nwhitehe@gmail.com> and others


    Released under the LGPL

    This module contains python bindings for FluidSynth.  FluidSynth is a
    software synthesizer for generating music.  It works like a MIDI
    synthesizer.  You load patches, set parameters, then send NOTEON and
    NOTEOFF events to play notes.  Instruments are defined in SoundFonts,
    generally files with the extension SF2.  FluidSynth can either be used
    to play audio itself, or you can call a function that returns chunks
    of audio data and output the data to the soundcard yourself.
    FluidSynth works on all major platforms, so pyFluidSynth should also.

================================================================================

"""

# Standard library modules
from ctypes import (CDLL, CFUNCTYPE, POINTER, Structure, byref, c_char, c_char_p, c_double,
                    c_float, c_int, c_short, c_size_t, c_uint, c_void_p, create_string_buffer)
from ctypes.util import find_library

# Third-party modules
from six import binary_type, iteritems, text_type

try:
    import numpy
except ImportError:
    numpy = None


# Constants

# Bump this up when changing the interface for users
api_version = '2.0'
# Used to encode / decode strings passed to / from C functions
DEFAULT_ENCODING = 'utf-8'
# Function call result
FLUID_OK = 0
FLUID_FAILED = -1
# Settings types
FLUID_NO_TYPE = -1  # Undefined type
FLUID_NUM_TYPE = 0  # Numeric (double)
FLUID_INT_TYPE = 1  # Integer
FLUID_STR_TYPE = 2  # String
FLUID_SET_TYPE = 3  # Set of values.
# MIDI router rule types
FLUID_MIDI_ROUTER_RULE_NOTE = 0              # MIDI note rule
FLUID_MIDI_ROUTER_RULE_CC = 1                # MIDI controller rule
FLUID_MIDI_ROUTER_RULE_PROG_CHANGE = 2       # MIDI program change rule
FLUID_MIDI_ROUTER_RULE_PITCH_BEND = 3        # MIDI pitch bend rule
FLUID_MIDI_ROUTER_RULE_CHANNEL_PRESSURE = 4  # MIDI channel pressure rule
FLUID_MIDI_ROUTER_RULE_KEY_PRESSURE = 5      # MIDI key pressure rule
# MIDI player state
FLUID_PLAYER_READY = 0  # Player is ready
FLUID_PLAYER_PLAYING = 1  # Player is currently playing
FLUID_PLAYER_DONE = 2  # Player is finished playing
# MIDI sequencer events
FLUID_SEQ_NOTE = 0  # Note event with duration
FLUID_SEQ_NOTEON = 1  # Note on event
FLUID_SEQ_NOTEOFF = 2  # Note off event
FLUID_SEQ_ALLSOUNDSOFF = 3  # All sounds off event
FLUID_SEQ_ALLNOTESOFF = 4  # All notes off event
FLUID_SEQ_BANKSELECT = 5  # Bank select message
FLUID_SEQ_PROGRAMCHANGE = 6  # Program change message
FLUID_SEQ_PROGRAMSELECT = 7  # Program select message
FLUID_SEQ_PITCHBEND = 8  # Pitch bend message
FLUID_SEQ_PITCHWHEELSENS = 9  # Pitch wheel sensitivity set message (since 1.1.0)
FLUID_SEQ_MODULATION = 10  # Modulation controller event
FLUID_SEQ_SUSTAIN = 11  # Sustain controller event
FLUID_SEQ_CONTROLCHANGE = 12  # MIDI control change event
FLUID_SEQ_PAN = 13  # Stereo pan set event
FLUID_SEQ_VOLUME = 14  # Volume set event
FLUID_SEQ_REVERBSEND = 15  # Reverb send set event
FLUID_SEQ_CHORUSSEND = 16  # Chorus send set event
FLUID_SEQ_TIMER = 17  # Timer event (useful for giving a callback at a certain time)
FLUID_SEQ_ANYCONTROLCHANGE = 18  # Any control change message (only used internally)
FLUID_SEQ_CHANNELPRESSURE = 19  # Channel aftertouch event (since 1.1.0)
FLUID_SEQ_KEYPRESSURE = 20  # Polyphonic aftertouch event (since 2.0.0)
FLUID_SEQ_SYSTEMRESET = 21  # System reset event (since 1.1.0)
FLUID_SEQ_UNREGISTERING = 22  # Called when a sequencer client is being unregistered (since 1.1.0)
# Driver names
AUDIO_DRIVER_NAMES = ("alsa, coreaudio, dart, dsound, file, jack, oss, portaudio, pulseaudio, "
                      "sdl2, sndman, waveout").split(", ")
MIDI_DRIVER_NAMES = "alsa_raw, alsa_seq, coremidi, jack, midishare, oss, winmidi".split(", ")
AUDIO_FILE_TYPES = ("aiff, au, auto, avr, caf, flac, htk, iff, mat, oga, paf, pvf, raw, sd2, sds, "
                    "sf, voc, w64, wav, xi").split(", ")

# A short circuited or expression to find the FluidSynth library
# (mostly needed for Windows distributions of libfluidsynth supplied with QSynth)
lib = (find_library('fluidsynth') or
       find_library('libfluidsynth') or
       find_library('fluidsynth-2') or
       find_library('libfluidsynth-2') or
       find_library('fluidsynth-1') or
       find_library('libfluidsynth-1') or
       # The basename of the DLL of certain fluidsynth 1.1.x
       # Windows builds has a '-7' suffix
       find_library('fluidsynth-7') or
       find_library('libfluidsynth-7'))

if lib is None:
    raise ImportError("Couldn't find the FluidSynth library.")

# Dynamically link the FluidSynth library
_fl = CDLL(lib)


# Helper function for declaring C function argument and return types
def cfunc(name, restype, *argtypes):
    try:
        func = getattr(_fl, name)
        if argtypes:
            func.argtypes = [(arg[1] if isinstance(arg, tuple) else arg) for arg in argtypes]
        func.restype = restype
    except AttributeError:
        func = None
        setattr(_fl, name, None)

    return func


# Function prototypes for C versions of functions

# General
cfunc('fluid_free',
      None,
      ('ptr', c_void_p))

# Fluid settings
cfunc('new_fluid_settings',
      c_void_p)
cfunc('fluid_settings_get_type',
      c_int,
      ('settings', c_void_p),
      ('name', c_char_p))
cfunc('fluid_settings_copystr',
      c_int,
      ('settings', c_void_p),
      ('name', c_char_p),
      ('str', c_char_p),
      ('len', c_int))
cfunc('fluid_settings_getnum',
      c_int,
      ('settings', c_void_p),
      ('name', c_char_p),
      ('val', POINTER(c_double)))
cfunc('fluid_settings_getint',
      c_int,
      ('settings', c_void_p),
      ('name', c_char_p),
      ('val', POINTER(c_int)))
cfunc('fluid_settings_setstr',
      c_int,
      ('settings', c_void_p),
      ('name', c_char_p),
      ('str', c_char_p))
cfunc('fluid_settings_setnum',
      c_int,
      ('settings', c_void_p),
      ('name', c_char_p),
      ('val', c_double))
cfunc('fluid_settings_setint',
      c_int,
      ('settings', c_void_p),
      ('name', c_char_p),
      ('val', c_int))
cfunc('delete_fluid_settings',
      None,
      ('settings', c_void_p))

# Fluid synth
cfunc('new_fluid_synth',
      c_void_p,
      ('settings', c_void_p))
cfunc('delete_fluid_synth',
      None,
      ('synth', c_void_p))
# Soundfont handling
cfunc('fluid_synth_sfload',
      c_int,
      ('synth', c_void_p),
      ('filename', c_char_p),
      ('update_midi_presets', c_int))
cfunc('fluid_synth_sfunload',
      c_int,
      ('synth', c_void_p),
      ('sfid', c_int),
      ('update_midi_presets', c_int))
cfunc('fluid_synth_get_sfont_by_id',
      c_void_p,
      ('synth', c_void_p),
      ('id', c_int))
cfunc('fluid_synth_sfont_select',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('sfid', c_int))
# MIDI program handling
cfunc('fluid_synth_program_select',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('sfid', c_int),
      ('bank', c_int),
      ('preset', c_int))
cfunc('fluid_synth_unset_program',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int))
cfunc('fluid_synth_get_program',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('sfont_id', POINTER(c_int)),
      ('bank_num', POINTER(c_int)),
      ('preset_num', POINTER(c_int)))
# MIDI events
cfunc('fluid_synth_noteon',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('key', c_int),
      ('vel', c_int))
cfunc('fluid_synth_noteoff',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('key', c_int))
cfunc('fluid_synth_pitch_bend',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('val', c_int))
cfunc('fluid_synth_cc',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('ctrl', c_int),
      ('val', c_int))
cfunc('fluid_synth_get_cc',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('num', c_int),
      ('pval', POINTER(c_int)))
cfunc('fluid_synth_program_change',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('prg', c_int))
cfunc('fluid_synth_bank_select',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('bank', c_int))
cfunc('fluid_synth_all_notes_off',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int))
# Reset functions
cfunc('fluid_synth_program_reset',
      c_int,
      ('synth', c_void_p))
cfunc('fluid_synth_system_reset',
      c_int,
      ('synth', c_void_p))
# Sample generation
cfunc('fluid_synth_write_float',
      c_int,
      ('synth', c_void_p),
      ('len', c_int),
      ('lbuf', c_void_p),
      ('loff', c_int),
      ('lincr', c_int),
      ('rbuf', c_void_p),
      ('roff', c_int),
      ('rincr', c_int))
cfunc('fluid_synth_write_s16',
      c_int,
      ('synth', c_void_p),
      ('len', c_int),
      ('lbuf', c_void_p),
      ('loff', c_int),
      ('lincr', c_int),
      ('rbuf', c_void_p),
      ('roff', c_int),
      ('rincr', c_int))
# Misc
cfunc('fluid_synth_handle_midi_event',
      c_int,
      ('data', c_void_p),
      ('event', c_void_p))

# Reverb
cfunc('fluid_synth_get_reverb_roomsize',
      c_double,
      ('synth', c_void_p))
cfunc('fluid_synth_get_reverb_damp',
      c_double,
      ('synth', c_void_p))
cfunc('fluid_synth_get_reverb_level',
      c_double,
      ('synth', c_void_p))
cfunc('fluid_synth_get_reverb_width',
      c_double,
      ('synth', c_void_p))
cfunc('fluid_synth_set_reverb_roomsize',
      c_int,
      ('synth', c_void_p),
      ('roomsize', c_double))
cfunc('fluid_synth_set_reverb_damp',
      c_int,
      ('synth', c_void_p),
      ('damping', c_double))
cfunc('fluid_synth_set_reverb_level',
      c_int,
      ('synth', c_void_p),
      ('level', c_double))
cfunc('fluid_synth_set_reverb_width',
      c_int,
      ('synth', c_void_p),
      ('width', c_double))
cfunc('fluid_synth_set_reverb',
      c_int,
      ('synth', c_void_p),
      ('roomsize', c_double),
      ('damping', c_double),
      ('width', c_double),
      ('level', c_double))

if not _fl.fluid_synth_set_reverb:
    cfunc('fluid_synth_set_reverb_full',
          c_int,
          ('synth', c_void_p),
          ('set', c_int),
          ('roomsize', c_double),
          ('damping', c_double),
          ('width', c_double),
          ('level', c_double))

# Chorus
cfunc('fluid_synth_get_chorus_nr',
      c_int,
      ('synth', c_void_p))
cfunc('fluid_synth_get_chorus_level',
      c_double,
      ('synth', c_void_p))
cfunc('fluid_synth_get_chorus_type',
      c_int,
      ('synth', c_void_p))
cfunc('fluid_synth_set_chorus_nr',
      c_int,
      ('synth', c_void_p),
      ('nr', c_int))
cfunc('fluid_synth_set_chorus_level',
      c_int,
      ('synth', c_void_p),
      ('level', c_double))
cfunc('fluid_synth_set_chorus_type',
      c_int,
      ('synth', c_void_p),
      ('type', c_int))
cfunc('fluid_synth_set_chorus_speed',
      c_int,
      ('synth', c_void_p),
      ('speed', c_double))
cfunc('fluid_synth_set_chorus_depth',
      c_int,
      ('synth', c_void_p),
      ('depth', c_double))
cfunc('fluid_synth_get_chorus_speed',
      c_double,
      ('synth', c_void_p))
cfunc('fluid_synth_get_chorus_depth',
      c_double,
      ('synth', c_void_p))
cfunc('fluid_synth_set_chorus',
      c_int,
      ('synth', c_void_p),
      ('nr', c_int),
      ('level', c_double),
      ('speed', c_double),
      ('depth_ms', c_double),
      ('type', c_int))

if not _fl.fluid_synth_set_chorus:
    cfunc('fluid_synth_set_chorus_full',
          c_int,
          ('synth', c_void_p),
          ('set', c_int),
          ('nr', c_int),
          ('level', c_double),
          ('speed', c_double),
          ('depth_ms', c_double),
          ('type', c_int))

if not _fl.fluid_synth_get_chorus_speed:
    _fl.fluid_synth_get_chorus_speed = cfunc('fluid_synth_get_chorus_speed_Hz',
                                             c_double,
                                             ('synth', c_void_p))


if not _fl.fluid_synth_get_chorus_depth:
    _fl.fluid_synth_get_chorus_depth = cfunc('fluid_synth_get_chorus_depth_ms',
                                             c_double,
                                             ('synth', c_void_p))

cfunc('fluid_synth_set_midi_router',
      None,
      ('synth', c_void_p),
      ('router', c_void_p))


class fluid_synth_channel_info_t(Structure):
    _fields_ = [
        ('assigned', c_int),
        ('sfont_id', c_int),
        ('bank', c_int),
        ('program', c_int),
        ('name', c_char * 32),
        ('reserved', c_char * 32)]


cfunc('fluid_synth_get_channel_info',
      c_int,
      ('synth', c_void_p),
      ('chan', c_int),
      ('info', POINTER(fluid_synth_channel_info_t)))

# Fluid audio driver
cfunc('new_fluid_audio_driver',
      c_void_p,
      ('settings', c_void_p),
      ('synth', c_void_p))
cfunc('delete_fluid_audio_driver',
      None,
      ('driver', c_void_p))

# Fluid MIDI driver
cfunc('new_fluid_midi_driver',
      c_void_p,
      ('settings', c_void_p),
      ('handler', CFUNCTYPE(POINTER(c_int), c_void_p, c_void_p)),
      ('event_handler_data', c_void_p))
cfunc('delete_fluid_midi_driver',
      None,
      ('driver', c_void_p))


# Fluid MIDI router
class fluid_midi_router_t(Structure):
    _fields_ = [
        ('synth', c_void_p),
        ('rules_mutex', c_void_p),
        ('rules', c_void_p * 6),
        ('free_rules', c_void_p),
        ('event_handler', c_void_p),
        ('event_handler_data', c_void_p),
        ('nr_midi_channels', c_int),
        ('cmd_rule', c_void_p),
        ('cmd_rule_type', POINTER(c_int))]


cfunc('new_fluid_midi_router',
      POINTER(fluid_midi_router_t),
      ('settings', c_void_p),
      ('handler', CFUNCTYPE(c_int, c_void_p, c_void_p)),
      ('event_handler_data', c_void_p))
cfunc('fluid_midi_router_handle_midi_event',
      c_int,
      ('data', c_void_p),
      ('event', c_void_p))
cfunc('fluid_midi_dump_prerouter',
      c_int,
      ('data', c_void_p),
      ('event', c_void_p))
cfunc('fluid_midi_dump_postrouter',
      c_int,
      ('data', c_void_p),
      ('event', c_void_p))
cfunc('fluid_midi_router_clear_rules',
      c_int,
      ('router', POINTER(fluid_midi_router_t)))
cfunc('fluid_midi_router_set_default_rules',
      c_int,
      ('router', POINTER(fluid_midi_router_t)))
cfunc('fluid_midi_router_add_rule',
      c_int,
      ('router', POINTER(fluid_midi_router_t)),
      ('rule', c_void_p),
      ('type', c_int))
cfunc('delete_fluid_midi_router',
      c_int,
      ('router', POINTER(fluid_midi_router_t)))

# Fluid MIDI router rules
cfunc('new_fluid_midi_router_rule',
      c_void_p)
cfunc('fluid_midi_router_rule_set_chan',
      None,
      ('rule', c_void_p),
      ('min', c_int),
      ('max', c_int),
      ('mul', c_float),
      ('add', c_int))
cfunc('fluid_midi_router_rule_set_param1',
      None,
      ('rule', c_void_p),
      ('min', c_int),
      ('max', c_int),
      ('mul', c_float),
      ('add', c_int))
cfunc('fluid_midi_router_rule_set_param2',
      None,
      ('rule', c_void_p),
      ('min', c_int),
      ('max', c_int),
      ('mul', c_float),
      ('add', c_int))
cfunc('delete_fluid_midi_router_rule',
      c_int,
      ('rule', c_void_p))

# Command handler
if _fl.fluid_synth_set_midi_router:
    cfunc('new_fluid_cmd_handler',
          c_void_p,
          ('synth', c_void_p))
else:
    cfunc('new_fluid_cmd_handler',
          c_void_p,
          ('synth', c_void_p),
          ('router', c_void_p))

cfunc('delete_fluid_cmd_handler',
      c_void_p,
      ('handler', c_void_p))

# Preset handling
cfunc('fluid_preset_get_name',
      c_char_p,
      ('preset', c_void_p))
cfunc('fluid_sfont_get_preset',
      c_void_p,
      ('sfont', c_void_p),
      ('banknum', c_int),
      ('prognum', c_int))

# Fluid file renderer
cfunc('new_fluid_file_renderer',
      c_void_p,
      ('synth', c_void_p))
cfunc('fluid_file_renderer_process_block',
      c_int,
      ('dev', c_void_p))
cfunc('fluid_file_set_encoding_quality',
      c_int,
      ('dev', c_void_p),
      ('q', c_double))
cfunc('delete_fluid_file_renderer',
      c_void_p,
      ('dev', c_void_p))

# Fluid MIDI player
cfunc('new_fluid_player',
      c_void_p,
      ('synth', c_void_p))
cfunc('fluid_player_add',
      c_int,
      ('player', c_void_p),
      ('midifile', c_char_p))
cfunc('fluid_player_add_mem',
      c_int,
      ('player', c_void_p),
      ('buffer', c_void_p),
      ('len', c_size_t))
cfunc('fluid_player_get_bpm',
      c_int,
      ('player', c_void_p))
cfunc('fluid_player_get_midi_tempo',
      c_int,
      ('player', c_void_p))
cfunc('fluid_player_get_status',
      c_int,
      ('player', c_void_p))
cfunc('fluid_player_get_current_tick',
      c_int,
      ('player', c_void_p))
cfunc('fluid_player_get_total_ticks',
      c_int,
      ('player', c_void_p))
cfunc('fluid_player_join',
      c_int,
      ('player', c_void_p))
cfunc('fluid_player_play',
      c_int,
      ('player', c_void_p))
cfunc('fluid_player_seek',
      c_int,
      ('player', c_void_p),
      ('ticks', c_int))
cfunc('fluid_player_set_loop',
      c_int,
      ('player', c_void_p),
      ('loop', c_int))
cfunc('fluid_player_set_bpm',
      c_int,
      ('player', c_void_p),
      ('bpm', c_int))
cfunc('fluid_player_set_midi_tempo',
      c_int,
      ('player', c_void_p),
      ('tempo', c_int))
cfunc('fluid_player_stop',
      c_int,
      ('player', c_void_p))
cfunc('delete_fluid_player',
      c_void_p,
      ('player', c_void_p))

# Fluid sequencer
cfunc('new_fluid_sequencer2',
      c_void_p,
      ('use_system_timer', c_int))
cfunc('fluid_sequencer_process',
      None,
      ('seq', c_void_p),
      ('msec', c_uint))
cfunc('fluid_sequencer_register_fluidsynth',
      c_short,
      ('seq', c_void_p),
      ('synth', c_void_p))
cfunc('fluid_sequencer_register_client',
      c_short,
      ('seq', c_void_p),
      ('name', c_char_p),
      ('callback', CFUNCTYPE(None, c_uint, c_void_p, c_void_p, c_void_p)),
      ('data', c_void_p))
cfunc('fluid_sequencer_unregister_client',
      None,
      ('seq', c_void_p),
      ('id', c_short))
cfunc('fluid_sequencer_get_tick',
      c_uint,
      ('seq', c_void_p))
cfunc('fluid_sequencer_set_time_scale',
      None,
      ('seq', c_void_p),
      ('scale', c_double))
cfunc('fluid_sequencer_get_time_scale',
      c_double,
      ('seq', c_void_p))
cfunc('fluid_sequencer_send_now',
      None,
      ('seq', c_void_p),
      ('evt', c_void_p))
cfunc('fluid_sequencer_send_at',
      c_int,
      ('seq', c_void_p),
      ('evt', c_void_p),
      ('time', c_uint),
      ('absolute', c_int))
cfunc('fluid_sequencer_remove_events',
      None,
      ('seq', c_void_p),
      ('source', c_short, 1),
      ('dest', c_short),
      ('type', c_int))
cfunc('fluid_sequencer_add_midi_event_to_buffer',
      c_int,
      ('data', c_void_p),
      ('event', c_void_p))
cfunc('delete_fluid_sequencer',
      None,
      ('seq', c_void_p))

# Fluid events
cfunc('new_fluid_event',
      c_void_p)
cfunc('fluid_event_set_source',
      None,
      ('evt', c_void_p),
      ('src', c_void_p))
cfunc('fluid_event_set_dest',
      None,
      ('evt', c_void_p),
      ('dest', c_void_p))
cfunc('fluid_event_timer',
      None,
      ('evt', c_void_p),
      ('data', c_void_p))
cfunc('fluid_event_note',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('key', c_short),
      ('vel', c_short),
      ('duration', c_uint))
cfunc('fluid_event_noteon',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('key', c_short),
      ('vel', c_short))
cfunc('fluid_event_noteoff',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('key', c_short))
cfunc('fluid_event_all_sounds_off',
      None,
      ('evt', c_void_p),
      ('channel', c_int))
cfunc('fluid_event_all_notes_off',
      None,
      ('evt', c_void_p),
      ('channel', c_int))
cfunc('fluid_event_bank_select',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('bank_num', c_short))
cfunc('fluid_event_program_change',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_program_select',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('sfont_id', c_uint),
      ('bank_num', c_short),
      ('preset_num', c_short))
cfunc('fluid_event_control_change',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('control', c_short),
      ('val', c_short))
cfunc('fluid_event_pitch_bend',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('pitch', c_int))
cfunc('fluid_event_pitch_wheelsens',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('value', c_short))
cfunc('fluid_event_modulation',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_sustain',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_pan',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_volume',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_reverb_send',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_chorus_send',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_key_pressure',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('key', c_short),
      ('val', c_short))
cfunc('fluid_event_channel_pressure',
      None,
      ('evt', c_void_p),
      ('channel', c_int),
      ('val', c_short))
cfunc('fluid_event_system_reset',
      None,
      ('evt', c_void_p))
cfunc('fluid_event_any_control_change',
      None,
      ('evt', c_void_p),
      ('channel', c_int))
cfunc('fluid_event_unregistering',
      None,
      ('evt', c_void_p))
cfunc('delete_fluid_event',
      None,
      ('evt', c_void_p))


# (Internal) Helper functions

def _d(s, encoding=DEFAULT_ENCODING):
    if isinstance(s, binary_type) and encoding:
        return s.decode(encoding)
    return s


def _e(s, encoding=DEFAULT_ENCODING):
    if isinstance(s, text_type) and encoding:
        return s.encode(encoding)
    return s


# Convenience functions

def fluid_synth_write_stereo(synth, nframes, dtype='int16'):
    """Return generated samples in stereo 16-bit or float format.

    :param synth: an instance of class Synth
    :param nframes: number of sample frames to generate
    :type nframes: ``int``
    :param dtype: data type of each sample frame
    :type dtype: ``numpy.dtype`` instance or ``str``
    :return: c_char or c_float array or one-dimenional NumPy array of interleaved samples
    :rtype: ``np.array(..., dtype=numpy.int16)``

    """
    if dtype == 'int16' or (numpy and dtype == numpy.int16):
        buf = create_string_buffer(nframes * 4)
        _fl.fluid_synth_write_s16(synth, nframes, buf, 0, 2, buf, 1, 2)
    elif dtype == 'float' or (numpy and dtype == numpy.float):
        buf = ( c_float * (nframes * 2) )()
        _fl.fluid_synth_write_float(synth, nframes, buf, 0, 2, buf, 1, 2)
    else:
        raise ValueError("Data type '%s' not supported. Is NumPy installed?" % dtype)

    if dtype and numpy:
        if dtype == 'float' or (numpy and dtype == numpy.float):
            return numpy.ndarray(nframes*2,'f',buf,order='C')
        else:
            return numpy.frombuffer(buf[:], dtype=dtype)
    else:
        return buf


def raw_audio_string(data):
    """Return a string of bytes to send to soundcard.

    Input is a numpy array of samples. Default output format is 16-bit signed
    (other formats not currently supported).

    """
    import numpy
    return (data.astype(numpy.int16)).tostring()


# Object-oriented interface, simplifies access to functions

class RouterRule:
    """Represents a FluidSynth MIDI router rule."""

    def __init__(self, type=FLUID_MIDI_ROUTER_RULE_NOTE, chan=None, param1=None, param2=None):
        self.type = type
        self.rule = _fl.new_fluid_midi_router_rule()

        if isinstance(chan, dict):
            self.set_chan(**chan)
        elif chan is not None:
            self.set_chan(*chan)

        if isinstance(param1, dict):
            self.set_param1(**param1)
        elif param1 is not None:
            self.set_param1(*param1)

        if isinstance(param2, dict):
            self.set_param2(**param2)
        elif param2 is not None:
            self.set_param2(*param2)

    def delete(self):
        if self.rule:
            _fl.delete_fluid_midi_router_rule(self.rule)
            self.rule = None

    def set_chan(self, min=0, max=15, mul=1.0, add=0):
        if self.rule:
            _fl.fluid_midi_router_rule_set_chan(self.rule, min, max, mul, add)

    def set_param1(self, min=0, max=127, mul=1.0, add=0):
        if self.rule:
            _fl.fluid_midi_router_rule_set_param1(self.rule, min, max, mul, add)

    def set_param2(self, min=0, max=127, mul=1.0, add=0):
        if self.rule:
            _fl.fluid_midi_router_rule_set_param2(self.rule, min, max, mul, add)


class BasePlayer(object):
    """Interface for the FluidSynth internal MIDI player."""

    def __init__(self, synth):
        """Initialize Player instance.

        :param synth: an instance of class Synth

        """
        self.synth = synth
        self.player = _fl.new_fluid_player(self.synth.synth)

    def delete(self):
        _fl.delete_fluid_player(self.player)

    def add(self, filename):
        """Add Standard MIDI File to the playlist.

        :param filename: SMF name / path
        :type filename: ``str``

        """
        return _fl.fluid_player_add(self.player, _e(filename))

    def add_mem(self, data):
        """Add SMF data to the playlist.

        :param data: SMF MIDI data
        :type data: ``bytes`` or ``bytearray``

        """
        return _fl.fluid_player_add_mem(self.player, data, len(data))

    def play(self):
        """Start playing."""
        return _fl.fluid_player_play(self.player)

    def join(self):
        """Wait until player is finished playing."""
        return _fl.fluid_player_join(self.player)

    def stop(self):
        """Stop playing."""
        return _fl.fluid_player_stop(self.player)

    @property
    def bpm(self):
        """Return current player tempo in BPM.

        :return: tempo in beats (quarter notes) per minute

        """
        return _fl.fluid_player_get_bpm(self.player)

    @bpm.setter
    def bpm(self, beats_per_minute):
        """Set player tempo in BPM.

        :param: beats_per_minute: tempo in beats (quarter notes) per minute
        :type beats_per_minute: ``int``

        """
        return _fl.fluid_player_set_bpm(self.player, beats_per_minute)

    @property
    def current_tick(self):
        """Return current player position.

        :return: position in MIDI ticks
        :rtype: ``int``

        """
        return _fl.fluid_player_get_current_tick(self.player)

    @current_tick.setter
    def current_tick(self, ticks):
        """Seek to given player position.

        :param ticks: position in MIDI ticks
        :type ticks: ``int``

        .. note: not supported in FluidSynth 1.x

        """
        if _fl.fluid_player_seek is None:
            raise NotImplementedError(
                "Seeking is not supported by the MIDI player in FluidSynth 1.x")

        return _fl.fluid_player_seek(self.player, ticks)

    @property
    def status(self):
        """Return player status.

        :return: ``FLUID_PLAYER_READY``, ``FLUID_PLAYER_PLAYING``,
            or ``FLUID_PLAYER_DONE`` constant value

        """
        return _fl.fluid_player_get_status(self.player)

    @property
    def tempo(self):
        """Return current player tempo.

        :return: tempo in microseconds per beat (quarter note)
        :rtype: ``int``

        """
        return _fl.fluid_player_get_midi_tempo(self.player)

    @tempo.setter
    def tempo(self, ms_per_quarter_note):
        """Set player tempo.

        :param ms_per_quarter_note: tempo in microseconds per beat (quarter note)
        :type ms_per_quarter_note: ``int``

        """
        return _fl.fluid_player_set_midi_tempo(self.player, ms_per_quarter_note)

    @property
    def total_ticks(self):
        """Return duration of current MIDI track in ticks.

        :rtype: ``int``

        """
        return _fl.fluid_player_get_total_ticks(self.player)


class Player(BasePlayer):
    reverb_presets = {
        # room size (0.0-1.2), damping (0.0-1.0), width (0.0-100.0), level (0.0-1.0)
        'Preset 1': (0.2, 0.0, 0.5, 0.9),
        'Preset 2': (0.4, 0.2, 0.5, 0.8),
        'Preset 3': (0.6, 0.4, 0.5, 0.7),
        'Preset 4': (0.8, 0.7, 0.5, 0.6),
        'Preset 5': (0.8, 0.0, 0.5, 0.5)
    }

    def play(self, offset=0):
        """Start playing at given offset.

        :param offset: time offset in MIDI ticks
        :type offset: ``int``

        """
        if offset != self.current_tick:
            self.seek(offset)

        return super(Player, self).play()

    def render(self, filename, filetype=None, quality=0.5, progress_callback=None):
        """Render MIDI file to audio file.

        :param filename: audio output file path and name
        'type filename: ``str``
        :param filetype: audio output file type
        :type filetype: ``str``
        :param quality: variable bit rate encoding quality when file type is
            ``flac`` or ``oga``
        :type quality: ``float`` (0.0 - 1.0)
        :param progress_callback: Python callable to call after each
            period-size block of sample frames has been written. Receives the
            filename, filetype, current total number of sample frames written
            and the period size as positional arguments in that order.
        :type progress_callback: callable with 4 positional args

        Possible choices for ``filetype`` are:

        aiff, au, auto, avr, caf, flac, htk, iff, mat, oga, paf, pvf, raw, sd2,
        sds, sf, voc, w64, wav, xi

        See also: http://www.fluidsynth.org/api/fluidsettings.xml#audio.file.type

        """
        self._set_render_settings(filename, filetype)
        renderer = _fl.new_fluid_file_renderer(self.synth.synth)
        if not renderer:
            raise OSError('Failed to create MIDI file renderer.')

        _fl.fluid_file_set_encoding_quality(renderer, quality)
        period_size = self.synth.setting('audio.period-size')
        num_samples = 0  # sample frame counter

        try:
            while self.status != FLUID_PLAYER_DONE:
                # Render one block
                if _fl.fluid_file_renderer_process_block(renderer) != FLUID_OK:
                    raise OSError('MIDI file renderer error.')

                num_samples += period_size
                if progress_callback:
                    # For progress reporting
                    progress_callback(filename, filetype, num_samples, period_size)
        finally:
            self.stop()
            self.join()
            self.synth.setting('player.timing-source', 'system')
            self.synth.setting("synth.lock-memory", 1)
            _fl.delete_fluid_file_renderer(renderer)

        return num_samples

    def _set_render_settings(self, filename, filetype=None):
        """Set audio file and audio file type and non-realtime rendering mode.

        Internal method called by ``Player.render()``.

        :param filename: audio output file path and name
        :type filename: ``str``
        :param filetype: audio output file type
        :type filetype: ``str``

        """
        if filetype is not None and filetype not in AUDIO_FILE_TYPES:
            raise OSError("Unknown file type '%s'." % filetype)

        self.synth.setting("audio.file.name", filename)
        self.synth.setting("player.timing-source", "sample")
        self.synth.setting("synth.lock-memory", 0)

        if filetype is not None:
            self.synth.setting("audio.file.type", filetype)

    def set_reverb(self, preset):
        """Change reverb preset.

        :param preset: reverb preset name (one of the ``Player.reverb_presets`` keys)
        :type preset: ``str``

        """
        self.synth.set_reverb(*self.reverb_presets[preset])

    def set_gain(self, gain):
        """Set synth master volume.

        :param gain: gain value ``0.2 - 10.0``
        :type gain: ``float``

        """
        self.synth.setting('synth.gain', float(gain))

    def stop(self):
        """Stop playing.

        Also triggers release phase of all currently sounding notes.

        """
        result = super(Player, self).stop()
        # Stop notes on all (-1) channels
        self.synth.all_notes_off(-1)
        return result


class Synth:
    """Represents a FluidSynth synthesizer."""

    def __init__(self, gain=0.2, samplerate=44100.0, channels=256, **kwargs):
        """Create new synthesizer object to control sound generation.

        Optional keyword arguments:

        :param gain: scale factor for audio output, default is 0.2. lower
            values give quieter output and allow more simultaneous notes
            without clipping
        :type gain: ``float``
        :param samplerate: output samplerate in Hz, default is 44100.0 Hz
            added capability for passing arbitrary fluid settings using args
        :type samplerate: ``float``
        :param channels: the number of MIDI channels the synthesizer supports.
            MIDI hardware is limited to 16 channels (the default value, but
            internally FluidSynth can use up to 256 channels, which can be
            mapped to different MIDI sources.
        :type channels: ``int``

        Additional keyword arguments are interpreted and applied as fluidsynth
        settings, i.e. the argument name is used as the setting name and its
        value as the setting value. Since most fluidsynth setting names are not
        valid Python identifiers and therefor can not be used as keyword
        arguments directly, you have to pass them via the ``**kwarg`` syntax.
        The values must have the proper type, i.e. ``int`` for
        ``FLUID_INT_TYPE` settings, `'float`` for ``FLUID_NUM_TYPE`` and
        ``str``  or ``bytes`` for ``FLUID_STR_TYPE`` settings.

        """
        self.settings = _fl.new_fluid_settings()
        self.setting('synth.gain', float(gain))
        self.setting('synth.sample-rate', float(samplerate))
        self.setting('synth.midi-channels', channels)

        for opt, val in iteritems(kwargs):
            self.setting(opt, val)

        self.synth = _fl.new_fluid_synth(self.settings)
        self.audio_driver = None
        self.midi_driver = None
        self.router = None
        self.cmd_handler = None

    def setting(self, opt, val=None):
        """Get/Set an arbitrary synth setting, type-smart."""
        opt = _e(opt)

        if val is None:
            stype = _fl.fluid_settings_get_type(self.settings, opt)

            if stype == FLUID_NUM_TYPE:
                val = c_double()
                response = _fl.fluid_settings_getnum(self.settings, opt, byref(val))
                return val.value if response == FLUID_OK else None
            elif stype == FLUID_INT_TYPE:
                val = c_int()
                response = _fl.fluid_settings_getint(self.settings, opt, byref(val))
                return val.value if response == FLUID_OK else None
            elif stype == FLUID_STR_TYPE:
                data = create_string_buffer(256)
                response = _fl.fluid_settings_copystr(self.settings, opt, data, 256)
                return _d(data.value) if response == FLUID_OK else None
            elif stype == FLUID_SET_TYPE:
                raise NotImplementedError("Setting of type FLUID_SET_TYPE not implemented.")
            elif stype == FLUID_NO_TYPE:
                raise KeyError("Setting '%s' does not exist." % _d(opt))
        elif isinstance(val, text_type):
            return _fl.fluid_settings_setstr(self.settings, opt, _e(val))
        elif isinstance(val, binary_type):
            return _fl.fluid_settings_setstr(self.settings, opt, val)
        elif isinstance(val, bool):
            return _fl.fluid_settings_setint(self.settings, opt, 1 if val else 0)
        elif isinstance(val, int):
            return _fl.fluid_settings_setint(self.settings, opt, val)
        elif isinstance(val, float):
            return _fl.fluid_settings_setnum(self.settings, opt, val)

    def start(self, driver=None, device=None, midi_driver=None, cmd_handler=False):
        """Start audio output driver in separate background thread.

        Call this function any time after creating the Synth object to start
        handling events.

        If you don't call this function, use ``get_samples()`` to generate
        samples.

        Optional keyword arguments:

        :param driver: which audio driver to use for output
        :type driver: ``str``
        :param device: the device to use for audio output
        :type device: ``str``
        :param midi_driver: which driver to use for MIDI input
        :type midi_driver: ``str``
        :param cmd_handler: whether to create a shell command handler
        :type cmd_handler: ``bool`` (default: ``False``)

        Possible choices for ``driver`` are:

        alsa, coreaudio, dart, dsound, file, jack, oss, portaudio, pulseaudio,
        sdl2, sndman, waveout

        See also: http://www.fluidsynth.org/api/fluidsettings.xml#audio.driver

        Possible choices for ``midi_driver`` are:

        alsa_raw, alsa_seq, coremidi, jack, midishare, oss, winmidi

        See also: http://www.fluidsynth.org/api/fluidsettings.xml#midi.driver

        Not all drivers will be available for every platform, it depends on
        which drivers were compiled into FluidSynth for your platform.

        """
        if driver is not None:
            if driver not in AUDIO_DRIVER_NAMES:
                raise ValueError("Unknown audio driver '%'." % driver)
            self.setting('audio.driver', driver)

            if device is not None:
                self.setting('audio.%s.device' % driver, device)

            self.audio_driver = _fl.new_fluid_audio_driver(self.settings, self.synth)

        if midi_driver is not None:
            if midi_driver not in MIDI_DRIVER_NAMES:
                raise ValueError("Unknown MIDI driver '%'." % midi_driver)
            self.setting('midi.driver', midi_driver)
            self.router = _fl.new_fluid_midi_router(
                self.settings,
                _fl.fluid_synth_handle_midi_event,
                self.synth)

            self.midi_driver = _fl.new_fluid_midi_driver(
                self.settings,
                _fl.fluid_midi_router_handle_midi_event,
                self.router)

        if cmd_handler:
            if _fl.fluid_synth_set_midi_router:
                _fl.fluid_synth_set_midi_router(self.synth, self.router)
            else:
                self.cmd_handler = _fl.new_fluid_cmd_handler(self.synth, self.router)

    def delete(self):
        if self.audio_driver is not None:
            _fl.delete_fluid_audio_driver(self.audio_driver)

        if self.midi_driver is not None:
            _fl.delete_fluid_midi_driver(self.midi_driver)

        if self.router is not None:
            _fl.delete_fluid_midi_router(self.router)

        if self.cmd_handler is not None:
            _fl.delete_fluid_cmd_handler(self.cmd_handler)

        _fl.delete_fluid_synth(self.synth)
        _fl.delete_fluid_settings(self.settings)

    def sfload(self, filename, update_midi_preset=0):
        """Load SoundFont and return its ID."""
        return _fl.fluid_synth_sfload(self.synth, _e(filename), update_midi_preset)

    def sfunload(self, sfid, update_midi_preset=0):
        """Unload a SoundFont and free memory it used."""
        return _fl.fluid_synth_sfunload(self.synth, sfid, update_midi_preset)

    def program_select(self, chan, sfid, bank, preset):
        """Select a program"""
        return _fl.fluid_synth_program_select(self.synth, chan, sfid, bank, preset)

    def program_unset(self, chan):
        """Set the preset of a MIDI channel to an unassigned state."""
        return _fl.fluid_synth_unset_program(self.synth, chan)

    def channel_info(self, chan):
        """Get soundfont, bank, prog, preset name of channel.

        Superceded by ``program_info`` and ``sfpreset_name``, included for
        backwards-compatibility.

        """
        if _fl.fluid_synth_get_channel_info:
            info = fluid_synth_channel_info_t()  # noqa:F821
            _fl.fluid_synth_get_channel_info(self.synth, chan, byref(info))
            return (info.sfont_id, info.bank, info.program, info.name)

        # fluidsynth-2
        (sfontid, banknum, prognum) = self.program_info(chan)
        return (sfontid, banknum, prognum, self.sfpreset_name(sfontid, banknum, prognum))

    def program_info(self, chan):
        sfontid = c_int()
        banknum = c_int()
        prognum = c_int()
        _fl.fluid_synth_get_program(self.synth, chan, byref(sfontid), byref(banknum),
                                    byref(prognum))
        return (sfontid.value, banknum.value, prognum.value)

    def sfpreset_name(self, sfid, bank, prog):
        """Return name of a soundfont preset."""
        if not _fl.fluid_preset_get_name:
            raise NotImplementedError(
                "Fluidsynth library does not provide required 'fluid_preset_get_name' function")

        sfont = _fl.fluid_synth_get_sfont_by_id(self.synth, sfid)
        preset = _fl.fluid_sfont_get_preset(sfont, bank, prog)
        return _d(_fl.fluid_preset_get_name(preset)) if preset else None

    def router_clear(self):
        if self.router is not None:
            _fl.fluid_midi_router_clear_rules(self.router)

    def router_default(self):
        if self.router is not None:
            _fl.fluid_midi_router_set_default_rules(self.router)

    def router_add_rule(self, rule):
        if self.router is None:
            return

        if rule.rule is None:
            raise ValueError("Can't add deleted RouterRule instance.")

        return _fl.fluid_midi_router_add_rule(self.router, rule.rule, rule.type)

    def set_reverb(self, roomsize=-1.0, damping=-1.0, width=-1.0, level=-1.0):
        """Set reverb parameters.

        :param roomsize: Reverb room size value (0.0-1.0)
        :type roomsize: ``float``
        :param damping: Reverb damping value (0.0-1.0)
        :type damping: ``float``
        :param width: Reverb width value (0.0-100.0)
        :type width: ``float``
        :param level: Reverb level value (0.0-1.0)
        :type level: ``float``

        """
        if _fl.fluid_synth_set_reverb:
            return _fl.fluid_synth_set_reverb(self.synth, roomsize, damping, width, level)

        # fluidsynth-1
        mask = 0
        if roomsize >= 0:
            mask += 0b0001
        if damping >= 0:
            mask += 0b0010
        if width >= 0:
            mask += 0b0100
        if level >= 0:
            mask += 0b1000

        return _fl.fluid_synth_set_reverb_full(self.synth, mask, roomsize, damping, width, level)

    def set_chorus(self, nr=-1, level=-1.0, speed=-1.0, depth=-1.0, type=-1):
        """Set chorus parameters.

        :param nr: Chorus voice count (0-99, CPU time consumption proportional
            to this value)
        :type nr: ``int``
        :param level: Chorus level (0.0-10.0)
        :type levl: ``float``
        :param speed: Chorus speed in Hz (0.29-5.0)
        :type speed: ``float``
        :param depth: Chorus depth (max value depends on synth sample rate,
           0.0-21.0 is safe for sample rate values up to 96KHz)
        :type depth: ``float``
        :param type: Chorus waveform type (0=sine, 1=triangle)
        :type type: ``int``

        """
        if _fl.fluid_synth_set_chorus:
            return _fl.fluid_synth_set_chorus(self.synth, nr, level, speed, depth, type)

        # fluidsynth-1
        mask = 0
        if nr >= 0:
            mask += 0b00001
        if level >= 0:
            mask += 0b00010
        if speed >= 0:
            mask += 0b00100
        if depth >= 0:
            mask += 0b01000
        if type >= 0:
            mask += 0b10000

        return _fl.fluid_synth_set_chorus_full(self.synth, mask, nr, level, speed, depth, type)

    def set_reverb_roomsize(self, roomsize):
        return _fl.fluid_synth_set_reverb_roomsize(self.synth, roomsize)

    def set_reverb_damp(self, damp):
        return _fl.fluid_synth_set_reverb_damp(self.synth, damp)

    def set_reverb_level(self, level):
        return _fl.fluid_synth_set_reverb_level(self.synth, level)

    def set_reverb_width(self, width):
        return _fl.fluid_synth_set_reverb_width(self.synth, width)

    def set_chorus_nr(self, nr):
        return _fl.fluid_synth_set_chorus_nr(self.synth, nr)

    def set_chorus_level(self, level):
        return _fl.fluid_synth_set_reverb_level(self.synth, level)

    def set_chorus_speed(self, speed):
        return _fl.fluid_synth_set_chorus_speed(self.synth, speed)

    def set_chorus_depth(self, depth):
        return _fl.fluid_synth_set_chorus_depth(self.synth, depth)

    def set_chorus_type(self, type):
        return _fl.fluid_synth_set_chorus_type(self.synth, type)

    def get_reverb_roomsize(self):
        return _fl.fluid_synth_get_reverb_roomsize(self.synth)

    def get_reverb_damp(self):
        return _fl.fluid_synth_get_reverb_damp(self.synth)

    def get_reverb_level(self):
        return _fl.fluid_synth_get_reverb_level(self.synth)

    def get_reverb_width(self):
        return _fl.fluid_synth_get_reverb_width(self.synth)

    def get_chorus_nr(self):
        return _fl.fluid_synth_get_chorus_nr(self.synth)

    def get_chorus_level(self):
        return _fl.fluid_synth_get_reverb_level(self.synth)

    def get_chorus_type(self):
        return _fl.fluid_synth_get_chorus_type(self.synth)

    def get_chorus_speed(self):
        return _fl.fluid_synth_get_chorus_speed(self.synth)

    def get_chorus_depth(self):
        return _fl.fluid_synth_get_chorus_depth(self.synth)

    def noteon(self, chan, key, vel):
        """Play a note."""
        if key < 0 or key > 128:
            return False
        if chan < 0:
            return False
        if vel < 0 or vel > 128:
            return False
        return _fl.fluid_synth_noteon(self.synth, chan, key, vel)

    def noteoff(self, chan, key):
        """Stop a note."""
        if key < 0 or key > 128:
            return False

        if chan < 0:
            return False

        return _fl.fluid_synth_noteoff(self.synth, chan, key)

    def pitch_bend(self, chan, val):
        """Adjust pitch of a playing channel by small amounts.

        * A pitch bend value of 0 is no pitch change from default.
        * A value of -2048 is 1 semitone down.
        * A value of 2048 is 1 semitone up.

        Maximum values are -8192 to +8192 (transposing by 4 semitones).

        """
        return _fl.fluid_synth_pitch_bend(self.synth, chan, val + 8192)

    def cc(self, chan, ctrl, val):
        """Send control change value.

        The controls that are recognized are dependent on the SoundFont.
        Values are always 0 to 127. Typical controls include:

          1 : vibrato
          7 : volume
          10 : pan (left to right)
          11 : expression (soft to loud)
          64 : sustain
          91 : reverb
          93 : chorus

        """
        return _fl.fluid_synth_cc(self.synth, chan, ctrl, val)

    def get_cc(self, chan, num):
        i = c_int()
        _fl.fluid_synth_get_cc(self.synth, chan, num, byref(i))
        return i.value

    def program_change(self, chan, prg):
        """Change the program."""
        return _fl.fluid_synth_program_change(self.synth, chan, prg)

    def bank_select(self, chan, bank):
        """Choose a bank."""
        return _fl.fluid_synth_bank_select(self.synth, chan, bank)

    def sfont_select(self, chan, sfid):
        """Choose a SoundFont."""
        return _fl.fluid_synth_sfont_select(self.synth, chan, sfid)

    def program_reset(self):
        """Reset the programs on all channels."""
        return _fl.fluid_synth_program_reset(self.synth)

    def system_reset(self):
        """Stop all notes and reset all programs."""
        return _fl.fluid_synth_system_reset(self.synth)

    def all_notes_off(self, chan):
        """Turn off all notes on a MIDI channel (put them into release phase)."""
        return _fl.fluid_synth_all_notes_off(self.synth, chan)

    def get_samples(self, len=1024, dtype='float'):
        """Generate audio samples.

        The return value will be a NumPy array containing the given length of
        audio samples. If the synth is set to stereo output (the default) the
        array will be size 2 * len.

        """
        return fluid_synth_write_stereo(self.synth, len, dtype)


class Sequencer:
    def __init__(self, time_scale=1000, use_system_timer=True):
        """Create new sequencer object to control and schedule timing of midi events.

        Optional keyword arguments:

        :param time_scale: ticks per second, defaults to 1000
        :param use_system_timer: whether the sequencer should advance by itself

        """
        self.client_callbacks = []
        self.sequencer = _fl.new_fluid_sequencer2(use_system_timer)
        _fl.fluid_sequencer_set_time_scale(self.sequencer, time_scale)

    def register_fluidsynth(self, synth):
        """Registers a synthesizer as a destination client of the sequencer.

        :param synth: an instance of class Synth
        :return: Sequencer client ID
        :rytpe: ``int``

        """
        client_id = _fl.fluid_sequencer_register_fluidsynth(self.sequencer, synth.synth)

        if client_id == FLUID_FAILED:
            raise OSError("Registering fluid synth failed.")

        return client_id

    def register_client(self, name, callback, data=None):
        c_callback = CFUNCTYPE(None, c_uint, c_void_p, c_void_p, c_void_p)(callback)
        client_id = _fl.fluid_sequencer_register_client(self.sequencer, _e(name), c_callback, data)

        if client_id == FLUID_FAILED:
            raise OSError("Registering client failed.")

        # Store in a list to prevent garbage collection
        self.client_callbacks.append(c_callback)
        return client_id

    def note(self, time, channel, key, velocity, duration, source=-1, dest=-1, absolute=True):
        evt = self._create_event(source, dest)
        _fl.fluid_event_note(evt, channel, key, velocity, duration)
        self._schedule_event(evt, time, absolute)
        _fl.delete_fluid_event(evt)

    def note_on(self, time, channel, key, velocity=127, source=-1, dest=-1, absolute=True):
        evt = self._create_event(source, dest)
        _fl.fluid_event_noteon(evt, channel, key, velocity)
        self._schedule_event(evt, time, absolute)
        _fl.delete_fluid_event(evt)

    def note_off(self, time, channel, key, source=-1, dest=-1, absolute=True):
        evt = self._create_event(source, dest)
        _fl.fluid_event_noteoff(evt, channel, key)
        self._schedule_event(evt, time, absolute)
        _fl.delete_fluid_event(evt)

    def timer(self, time, data=None, source=-1, dest=-1, absolute=True):
        evt = self._create_event(source, dest)
        _fl.fluid_event_timer(evt, data)
        self._schedule_event(evt, time, absolute)
        _fl.delete_fluid_event(evt)

    def _create_event(self, source=-1, dest=-1):
        evt = _fl.new_fluid_event()
        _fl.fluid_event_set_source(evt, source)
        _fl.fluid_event_set_dest(evt, dest)
        return evt

    def _schedule_event(self, evt, time=None, absolute=True):
        if time is None:
            response = _fl.fluid_sequencer_send_now(self.sequencer, evt)
        else:
            response = _fl.fluid_sequencer_send_at(self.sequencer, evt, time, 1 if absolute else 0)

        if response == FLUID_FAILED:
            raise OSError("Scheduling event failed.")

    def get_tick(self):
        return _fl.fluid_sequencer_get_tick(self.sequencer)

    def process(self, msec):
        _fl.fluid_sequencer_process(self.sequencer, msec)

    def delete(self):
        _fl.delete_fluid_sequencer(self.sequencer)
