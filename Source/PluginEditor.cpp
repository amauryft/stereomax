#include "PluginEditor.h"
#include "BinaryData.h"

static std::vector<std::byte> toBytes (const char* data, int size)
{
    std::vector<std::byte> v ((size_t) size);
    std::memcpy (v.data(), data, (size_t) size);
    return v;
}

juce::WebBrowserComponent::Options SpreadEditor::makeOptions()
{
    // Build one relay per parameter (name = parameter ID) before the browser is created.
    for (auto* p : proc.getParameters())
    {
        auto* rp = dynamic_cast<juce::RangedAudioParameter*> (p);
        if (rp == nullptr) continue;
        if (dynamic_cast<juce::AudioParameterBool*> (p) != nullptr)
        {
            toggleRelays.push_back (std::make_unique<juce::WebToggleButtonRelay> (rp->getParameterID()));
            toggleParams.push_back (rp);
        }
        else
        {
            sliderRelays.push_back (std::make_unique<juce::WebSliderRelay> (rp->getParameterID()));
            sliderParams.push_back (rp);
        }
    }

    auto opts = juce::WebBrowserComponent::Options{}
                    .withBackend (juce::WebBrowserComponent::Options::Backend::defaultBackend)
                    .withNativeIntegrationEnabled()
                    .withKeepPageLoadedWhenBrowserIsHidden()
                    .withResourceProvider ([this] (const auto& url) { return getResource (url); });
    for (auto& r : sliderRelays) opts = opts.withOptionsFrom (*r);
    for (auto& r : toggleRelays) opts = opts.withOptionsFrom (*r);
    return opts;
}

SpreadEditor::SpreadEditor (SpreadProcessor& p)
    : AudioProcessorEditor (&p), proc (p), web (makeOptions())
{
    for (size_t i = 0; i < sliderRelays.size(); ++i)
        sliderAttachments.push_back (std::make_unique<juce::WebSliderParameterAttachment> (*sliderParams[i], *sliderRelays[i], nullptr));
    for (size_t i = 0; i < toggleRelays.size(); ++i)
        toggleAttachments.push_back (std::make_unique<juce::WebToggleButtonParameterAttachment> (*toggleParams[i], *toggleRelays[i], nullptr));

    addAndMakeVisible (web);
    web.goToURL (juce::WebBrowserComponent::getResourceProviderRoot());

    setResizable (true, true);
    setResizeLimits (820, 570, 2460, 1710);
    if (auto* c = getConstrainer()) c->setFixedAspectRatio (1640.0 / 1140.0);
    setSize (1312, 912);
    startTimerHz (30);
}

SpreadEditor::~SpreadEditor() { stopTimer(); }

void SpreadEditor::resized() { web.setBounds (getLocalBounds()); }

std::optional<juce::WebBrowserComponent::Resource> SpreadEditor::getResource (const juce::String& url)
{
    auto path = url.fromFirstOccurrenceOf ("/", false, false);
    if (path.isEmpty() || path == "index.html")
        return juce::WebBrowserComponent::Resource { toBytes (BinaryData::index_html, BinaryData::index_htmlSize), "text/html" };
    if (path == "juce/index.js")
        return juce::WebBrowserComponent::Resource { toBytes (BinaryData::index_js, BinaryData::index_jsSize), "text/javascript" };
    if (path == "juce/check_native_interop.js")
        return juce::WebBrowserComponent::Resource { toBytes (BinaryData::check_native_interop_js, BinaryData::check_native_interop_jsSize), "text/javascript" };
    return std::nullopt;
}

void SpreadEditor::timerCallback()
{
    auto* o = new juce::DynamicObject();
    o->setProperty ("inL", proc.mInL.load());
    o->setProperty ("inR", proc.mInR.load());
    o->setProperty ("outL", proc.mOutL.load());
    o->setProperty ("outR", proc.mOutR.load());
    o->setProperty ("mid", proc.mMid.load());
    o->setProperty ("side", proc.mSide.load());
    o->setProperty ("corr", proc.mCorr.load());
    o->setProperty ("inCorr", proc.mInCorr.load());
    o->setProperty ("pull", proc.mPull.load());

    juce::Array<juce::var> pts;
    const int count = 400;
    int w = proc.scopeWrite.load (std::memory_order_acquire);
    for (int i = 0; i < count; ++i)
    {
        int idx = (w - count + i + SpreadProcessor::scopeSize) % SpreadProcessor::scopeSize;
        pts.add (proc.scope[(size_t) (idx * 2)]);
        pts.add (proc.scope[(size_t) (idx * 2 + 1)]);
    }
    o->setProperty ("scope", pts);
    web.emitEventIfBrowserIsVisible ("meters", juce::var (o));
}
