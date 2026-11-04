cmake_minimum_required(VERSION 3.22)
project(Spread VERSION 0.3.2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(juce
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG 8.0.8
    GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(juce)

juce_add_plugin(Spread
    COMPANY_NAME "Mau Audio"
    BUNDLE_ID "com.mauaudio.superspread"
    PLUGIN_MANUFACTURER_CODE Mauf
    PLUGIN_CODE Sprd
    FORMATS AU VST3
    PRODUCT_NAME "SuperSpread"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    NEEDS_WEB_BROWSER TRUE
    AU_MAIN_TYPE kAudioUnitType_Effect
    VST3_CATEGORIES Fx Spatial
    COPY_PLUGIN_AFTER_BUILD FALSE)

juce_add_binary_data(SpreadUI SOURCES
    ui/index.html
    ${juce_SOURCE_DIR}/modules/juce_gui_extra/native/javascript/index.js
    ${juce_SOURCE_DIR}/modules/juce_gui_extra/native/javascript/check_native_interop.js)

target_sources(Spread PRIVATE
    Source/PluginProcessor.cpp
    Source/PluginEditor.cpp)

target_compile_definitions(Spread PUBLIC
    JUCE_WEB_BROWSER=1
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    JUCE_DISPLAY_SPLASH_SCREEN=0)

target_link_libraries(Spread
    PRIVATE
        SpreadUI
        juce::juce_audio_utils
        juce::juce_dsp
        juce::juce_gui_extra
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags)
