#pragma once
#include <juce_gui_extra/juce_gui_extra.h>
#include "PluginProcessor.h"

class SpreadEditor : public juce::AudioProcessorEditor, private juce::Timer
{
public:
    explicit SpreadEditor (SpreadProcessor&);
    ~SpreadEditor() override;
    void resized() override;

private:
    void timerCallback() override;
    std::optional<juce::WebBrowserComponent::Resource> getResource (const juce::String& url);
    juce::WebBrowserComponent::Options makeOptions();

    SpreadProcessor& proc;
    std::vector<std::unique_ptr<juce::WebSliderRelay>> sliderRelays;
    std::vector<std::unique_ptr<juce::WebToggleButtonRelay>> toggleRelays;
    std::vector<juce::RangedAudioParameter*> sliderParams, toggleParams;
    juce::WebBrowserComponent web;
    std::vector<std::unique_ptr<juce::WebSliderParameterAttachment>> sliderAttachments;
    std::vector<std::unique_ptr<juce::WebToggleButtonParameterAttachment>> toggleAttachments;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SpreadEditor)
};
