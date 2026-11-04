#pragma once
#include <juce_audio_processors/juce_audio_processors.h>
#include <juce_dsp/juce_dsp.h>
#include <array>
#include <atomic>

//==============================================================================
// Small DSP building blocks
struct Delay
{
    std::vector<float> buf; int w = 0; int mask = 0;
    void prepare (int maxSamples)
    {
        int n = 1; while (n < maxSamples + 4) n <<= 1;
        buf.assign ((size_t) n, 0.0f); mask = n - 1; w = 0;
    }
    void clear() { std::fill (buf.begin(), buf.end(), 0.0f); }
    void push (float x) { buf[(size_t) w] = x; w = (w + 1) & mask; }
    // d in samples (>= 1)
    float read (float d) const
    {
        float rp = (float) w - d;
        while (rp < 0) rp += (float) (mask + 1);
        int i0 = (int) rp; float fr = rp - (float) i0;
        float a = buf[(size_t) (i0 & mask)], b = buf[(size_t) ((i0 + 1) & mask)];
        return a + (b - a) * fr;
    }
};

struct Allpass
{
    Delay d; float g = 0.6f; float len = 100;
    void prepare (int maxS, float lenS, float gain) { d.prepare (maxS); len = lenS; g = gain; }
    float process (float x)
    {
        float del = d.read (len);
        float v = x + g * del;
        d.push (v);
        return del - g * v;
    }
};

// Doppler-style micro pitch shifter (two crossfaded taps)
struct MicroPitch
{
    Delay d; float phase = 0; float windowS = 1000;
    void prepare (double sr) { windowS = (float) (0.03 * sr); d.prepare ((int) windowS * 2 + 8); phase = 0; }
    float process (float x, float ratio)
    {
        d.push (x);
        float step = (1.0f - ratio) / windowS;
        phase += step; if (phase >= 1) phase -= 1; if (phase < 0) phase += 1;
        float p2 = phase + 0.5f; if (p2 >= 1) p2 -= 1;
        float g1 = std::sin (juce::MathConstants<float>::pi * phase);
        float g2 = std::sin (juce::MathConstants<float>::pi * p2);
        return d.read (2 + phase * windowS) * g1 + d.read (2 + p2 * windowS) * g2;
    }
};

struct Comb
{
    Delay d; float len = 1000, fb = 0.8f, damp = 0.3f, z = 0;
    void prepare (int lenS) { d.prepare (lenS + 4); len = (float) lenS; z = 0; }
    float process (float x)
    {
        float y = d.read (len);
        z = y * (1 - damp) + z * damp;
        d.push (x + z * fb);
        return y;
    }
};

struct OnePole
{
    float z = 0, a = 0;
    void set (double sr, float hz) { a = (float) std::exp (-2.0 * juce::MathConstants<double>::pi * hz / sr); }
    float lp (float x) { z = x + (z - x) * a; return z; }
};

//==============================================================================
class SpreadProcessor : public juce::AudioProcessor
{
public:
    SpreadProcessor();
    ~SpreadProcessor() override = default;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return "SuperSpread"; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 1.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram (int) override {}
    const juce::String getProgramName (int) override { return "Default"; }
    void changeProgramName (int, const juce::String&) override {}

    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

    juce::AudioProcessorValueTreeState apvts;
    double uiScale = 0.8;   // window size, remembered with the session
    juce::String uiTheme { "light" };
    static juce::AudioProcessorValueTreeState::ParameterLayout createLayout();

    // ---- metering for the UI
    std::atomic<float> mInL { 0 }, mInR { 0 }, mOutL { 0 }, mOutR { 0 }, mMid { 0 }, mSide { 0 };
    std::atomic<float> mCorr { 1 }, mPull { 0 }, mInCorr { 1 };
    static constexpr int scopeSize = 1024;
    std::array<float, scopeSize * 2> scope {};
    std::atomic<int> scopeWrite { 0 };

private:
    float p (const char* id) const { return apvts.getRawParameterValue (id)->load(); }
    bool b (const char* id) const { return p (id) > 0.5f; }

    double sr = 44100;
    Delay chDelay, haasDelay, combDelay, chorusDelay, beyondL, beyondR;
    MicroPitch up, down;
    std::array<Allpass, 4> ap;
    std::array<Comb, 8> roomCombs;
    std::array<Allpass, 4> roomAp;
    juce::dsp::LinkwitzRileyFilter<float> xo0, xo1, xo2;
    OnePole shuffleLp, beyondLpL, beyondLpR;
    float envFast = 0, envSlow = 0;
    double chorusPhase = 0, motionPhase = 0;
    float eLR = 0, eLL = 0, eRR = 0;   // guard detector (pre)
    float oLR = 0, oLL = 0, oRR = 0;   // output correlation
    float iLR = 0, iLL = 0, iRR = 0;   // input correlation
    float guardGain = 1;
    float pkInL = 0, pkInR = 0, pkOutL = 0, pkOutR = 0, rmsM = 0, rmsS = 0;
    int scopeDecim = 0;
    juce::SmoothedValue<float> smAmt, smMid, smSide, smGain, smMix;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SpreadProcessor)
};
