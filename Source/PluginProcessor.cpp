#include "PluginProcessor.h"
#include "PluginEditor.h"

using APVTS = juce::AudioProcessorValueTreeState;

static void addF (APVTS::ParameterLayout& l, const char* id, const char* name, float lo, float hi, float def, const char* unit = "")
{
    l.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { id, 1 }, name,
                                                         juce::NormalisableRange<float> (lo, hi), def,
                                                         juce::AudioParameterFloatAttributes().withLabel (unit)));
}
static void addB (APVTS::ParameterLayout& l, const char* id, const char* name, bool def)
{
    l.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { id, 1 }, name, def));
}

APVTS::ParameterLayout SpreadProcessor::createLayout()
{
    APVTS::ParameterLayout l;
    addF (l, "master", "Master", 0, 200, 100, "%");
    addB (l, "link_gen", "Link Generate", true);
    addB (l, "link_shape", "Link Shape", true);
    addB (l, "link_space", "Link Space", true);
    // Input
    addB (l, "in_on", "Input On", true);
    addF (l, "in_bal", "Balance", -100, 100, 0, "%");
    addF (l, "in_trim", "Trim", -12, 12, 0, "dB");
    addF (l, "in_dly", "Channel Delay", 0, 20, 0, "ms");
    addB (l, "in_phl", "Phase L", false);
    addB (l, "in_phr", "Phase R", false);
    addB (l, "in_swap", "Swap", false);
    addB (l, "in_mono", "Mono In", false);
    // Generate
    addB (l, "gen_on", "Generate On", true);
    addF (l, "gen_amt", "Amount", 0, 100, 60, "%");
    addF (l, "gen_time", "Time", 1, 40, 12, "ms");
    addF (l, "gen_cents", "Cents", 0, 25, 9, "ct");
    addF (l, "gen_rate", "Rate", 0.05f, 5, 0.6f, "Hz");
    addF (l, "gen_size", "Size", 0, 100, 30, "%");
    addB (l, "e_haas", "Haas", true);
    addB (l, "e_detune", "Detune", true);
    addB (l, "e_chorus", "Chorus", false);
    addB (l, "e_comb", "Comb", false);
    addB (l, "e_allpass", "Allpass", true);
    addB (l, "e_room", "Room", false);
    // Shape
    addB (l, "sh_on", "Shape On", true);
    addF (l, "sh_bass", "Bass Mono", 0, 300, 150, "Hz");
    addF (l, "sh_lo", "Lo-Mid Width", 0, 100, 35, "%");
    addF (l, "sh_hi", "Hi-Mid Width", 0, 100, 50, "%");
    addF (l, "sh_top", "High Width", 0, 100, 70, "%");
    addF (l, "sh_tilt", "Side Tilt", -100, 100, 0, "%");
    addF (l, "sh_drive", "Side Drive", 0, 100, 20, "%");
    addB (l, "solo_s", "Solo Side", false);
    addB (l, "solo_m", "Solo Mid", false);
    // Space
    addB (l, "sp_on", "Space On", true);
    addF (l, "sp_shuf", "Shuffle", 0, 6, 2, "dB");
    addF (l, "sp_tr", "Transient Width", 0, 200, 100, "%");
    addF (l, "sp_sus", "Sustain Width", 0, 200, 100, "%");
    addF (l, "sp_mot", "Motion Rate", 0.02f, 2, 0.2f, "Hz");
    addF (l, "sp_dep", "Motion Depth", 0, 100, 0, "%");
    addB (l, "sp_beyond", "Beyond", false);
    addB (l, "sp_sync", "Sync", false);
    // Guard
    addB (l, "gd_on", "Guard On", true);
    addB (l, "gd_auto", "Guard Auto", true);
    addF (l, "gd_thr", "Threshold", -0.5f, 0.5f, -0.05f);
    addF (l, "gd_rec", "Recovery", 0, 4, 2);
    addB (l, "gd_listen", "Listen", false);
    // Output
    addB (l, "out_on", "Output On", true);
    addF (l, "out_mid", "Mid", -12, 12, 0, "dB");
    addF (l, "out_side", "Side", -12, 12, 0, "dB");
    addF (l, "out_mix", "Mix", 0, 100, 100, "%");
    addF (l, "out_gain", "Output", -12, 12, 0, "dB");
    addB (l, "out_mono", "Mono", false);
    addB (l, "out_bypass", "Bypass", false);
    return l;
}

SpreadProcessor::SpreadProcessor()
    : AudioProcessor (BusesProperties()
                          .withInput ("Input", juce::AudioChannelSet::stereo(), true)
                          .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "SPREAD", createLayout())
{
}

bool SpreadProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    auto in = layouts.getMainInputChannelSet(), out = layouts.getMainOutputChannelSet();
    if (out != juce::AudioChannelSet::stereo()) return false;
    return in == juce::AudioChannelSet::stereo() || in == juce::AudioChannelSet::mono();
}

void SpreadProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    sr = sampleRate;
    auto ms = [this] (double m) { return (int) (m * 0.001 * sr); };
    chDelay.prepare (ms (25)); haasDelay.prepare (ms (45)); combDelay.prepare (ms (45));
    chorusDelay.prepare (ms (30)); beyondL.prepare (ms (2)); beyondR.prepare (ms (2));
    up.prepare (sr); down.prepare (sr);
    const float apMs[4] = { 4.7f, 7.3f, 11.1f, 17.3f };
    for (int i = 0; i < 4; ++i) ap[(size_t) i].prepare (ms (20), (float) (apMs[i] * 0.001 * sr), 0.6f);
    const float combMs[8] = { 25.3f, 26.9f, 28.9f, 30.7f, 25.9f, 27.5f, 29.6f, 31.3f };
    for (int i = 0; i < 8; ++i) roomCombs[(size_t) i].prepare (ms (combMs[i]));
    const float rApMs[4] = { 5.0f, 1.7f, 5.4f, 1.9f };
    for (int i = 0; i < 4; ++i) roomAp[(size_t) i].prepare (ms (8), (float) (rApMs[i] * 0.001 * sr), 0.5f);

    juce::dsp::ProcessSpec spec { sr, (juce::uint32) samplesPerBlock, 1 };
    for (auto* f : { &xo0, &xo1, &xo2 }) { f->prepare (spec); f->setType (juce::dsp::LinkwitzRileyFilterType::lowpass); }
    xo0.setCutoffFrequency (150); xo1.setCutoffFrequency (1200); xo2.setCutoffFrequency (6000);
    shuffleLp.set (sr, 700); beyondLpL.set (sr, 3000); beyondLpR.set (sr, 3000);
    envFast = envSlow = 0; guardGain = 1;
    for (auto* s : { &smAmt, &smMid, &smSide, &smGain, &smMix }) s->reset (sr, 0.03);
    smAmt.setCurrentAndTargetValue (0.6f); smMid.setCurrentAndTargetValue (1); smSide.setCurrentAndTargetValue (1);
    smGain.setCurrentAndTargetValue (1); smMix.setCurrentAndTargetValue (1);
}

void SpreadProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;
    const int n = buffer.getNumSamples();
    const int numIn = getTotalNumInputChannels();
    if (numIn == 1 && buffer.getNumChannels() > 1) buffer.copyFrom (1, 0, buffer, 0, 0, n);
    if (buffer.getNumChannels() < 2) return;
    float* L = buffer.getWritePointer (0);
    float* R = buffer.getWritePointer (1);

    // ---- master macro: scales the linked "amount" knobs
    const float master = p ("master") / 100.0f;
    auto norm = [this] (const char* id) { auto* prm = apvts.getParameter (id); return prm->getValue(); };
    auto denorm = [this] (const char* id, float v) { auto* prm = apvts.getParameter (id); return prm->convertFrom0to1 (juce::jlimit (0.0f, 1.0f, v)); };
    // Balanced master: one shared factor for every linked knob, so their ratios never change.
    // Up to 100% it scales down; above 100% it grows until the most-pushed linked knob reaches max at 200%.
    struct LinkDef { const char* id; const char* link; bool bipolar; };
    static const LinkDef linkDefs[] = { { "gen_amt", "link_gen", false }, { "gen_cents", "link_gen", false }, { "gen_size", "link_gen", false },
                                        { "sh_lo", "link_shape", false }, { "sh_hi", "link_shape", false }, { "sh_top", "link_shape", false },
                                        { "sh_tilt", "link_shape", true }, { "sh_drive", "link_shape", false },
                                        { "sp_shuf", "link_space", false }, { "sp_dep", "link_space", false } };
    float mGain = master;
    if (master > 1.0f)
    {
        float mx = 0;
        for (auto& d : linkDefs)
            if (b (d.link)) mx = juce::jmax (mx, d.bipolar ? std::abs (norm (d.id) - 0.5f) * 2.0f : norm (d.id));
        if (mx > 1e-4f) mGain = 1.0f + (master - 1.0f) * (1.0f / mx - 1.0f);
    }
    auto linked = [&] (const char* id, const char* link) { float v = norm (id); if (b (link)) v *= mGain; return denorm (id, v); };
    auto linkedBi = [&] (const char* id, const char* link) { float v = norm (id); if (b (link)) v = 0.5f + (v - 0.5f) * mGain; return denorm (id, v); };

    const bool inOn = b ("in_on"), genOn = b ("gen_on"), shOn = b ("sh_on"), spOn = b ("sp_on"), gdOn = b ("gd_on"), outOn = b ("out_on");
    // input
    const float bal = p ("in_bal") / 100.0f, trim = juce::Decibels::decibelsToGain (p ("in_trim"));
    const float chD = p ("in_dly") * 0.001f * (float) sr;
    const bool phL = b ("in_phl"), phR = b ("in_phr"), swap = b ("in_swap"), monoIn = b ("in_mono");
    // generate
    const float amt = linked ("gen_amt", "link_gen") / 100.0f;
    const float timeS = p ("gen_time") * 0.001f * (float) sr;
    const float cents = linked ("gen_cents", "link_gen");
    const float rate = p ("gen_rate");
    const float size = linked ("gen_size", "link_gen") / 100.0f;
    const bool eHaas = b ("e_haas"), eDet = b ("e_detune"), eCho = b ("e_chorus"), eComb = b ("e_comb"), eAp = b ("e_allpass"), eRoom = b ("e_room");
    const float ratioUp = std::pow (2.0f, cents / 1200.0f), ratioDn = std::pow (2.0f, -cents / 1200.0f);
    for (auto& c : roomCombs) c.fb = 0.70f + 0.25f * size;
    // shape
    const float bassHz = p ("sh_bass");
    const bool bassOn = bassHz >= 20.0f;
    xo0.setCutoffFrequency (bassOn ? bassHz : 20.0f);
    const float tilt = linkedBi ("sh_tilt", "link_shape") / 100.0f;
    float g[4];
    g[1] = 1 + linked ("sh_lo", "link_shape") / 100.0f;
    g[2] = 1 + linked ("sh_hi", "link_shape") / 100.0f;
    g[3] = 1 + linked ("sh_top", "link_shape") / 100.0f;
    for (int i = 1; i < 4; ++i) g[i] *= juce::jmax (0.0f, 1.0f + tilt * 0.5f * ((float) i - 2.0f));
    g[0] = bassOn ? 0.0f : g[1];
    const float drive = linked ("sh_drive", "link_shape") / 100.0f;
    const bool soloS = b ("solo_s"), soloM = b ("solo_m");
    // space
    const float shuf = juce::Decibels::decibelsToGain (linked ("sp_shuf", "link_space")) - 1.0f;
    const float trW = p ("sp_tr") / 100.0f, susW = p ("sp_sus") / 100.0f;
    float motRate = p ("sp_mot");
    if (b ("sp_sync"))
        if (auto* ph = getPlayHead())
            if (auto pos = ph->getPosition())
                if (auto bpm = pos->getBpm()) motRate = (float) (*bpm / 240.0); // one cycle per bar
    const float depth = linked ("sp_dep", "link_space") / 100.0f;
    const bool beyond = b ("sp_beyond");
    // guard
    const bool gAuto = b ("gd_auto"), listen = b ("gd_listen");
    const float thr = p ("gd_thr");
    const int rec = juce::jlimit (0, 4, (int) std::round (p ("gd_rec")));
    const float recMs[4] = { 100, 400, 800, 1500 };
    // output
    smAmt.setTargetValue (genOn ? amt : 0.0f);
    smMid.setTargetValue (outOn ? juce::Decibels::decibelsToGain (p ("out_mid")) : 1.0f);
    smSide.setTargetValue (outOn ? juce::Decibels::decibelsToGain (p ("out_side")) : 1.0f);
    smGain.setTargetValue (outOn ? juce::Decibels::decibelsToGain (p ("out_gain")) : 1.0f);
    smMix.setTargetValue (outOn ? p ("out_mix") / 100.0f : 1.0f);
    const bool monoOut = b ("out_mono"), bypass = b ("out_bypass");

    const float statA = (float) std::exp (-1.0 / (0.05 * sr));
    const float atkF = (float) std::exp (-1.0 / (0.001 * sr)), relF = (float) std::exp (-1.0 / (0.02 * sr));
    const float atkS = (float) std::exp (-1.0 / (0.03 * sr)), relS = (float) std::exp (-1.0 / (0.3 * sr));
    const float gAtk = (float) std::exp (-1.0 / (0.01 * sr));
    const float pkDecay = (float) std::exp (-1.0 / (0.3 * sr));
    const double chorusInc = rate / sr, motionInc = motRate / sr;
    const float twoPi = juce::MathConstants<float>::twoPi;

    for (int i = 0; i < n; ++i)
    {
        const float dryL = L[i], dryR = R[i];
        float l = dryL, r = dryR;

        // ---------------- INPUT
        if (inOn)
        {
            l *= trim; r *= trim;
            if (phL) l = -l;
            if (phR) r = -r;
            if (swap) std::swap (l, r);
            if (monoIn) { float m = 0.5f * (l + r); l = r = m; }
            l *= juce::jmin (1.0f, 1.0f - bal); r *= juce::jmin (1.0f, 1.0f + bal);
            chDelay.push (r);
            if (chD > 0.5f) r = chDelay.read (chD);
        }
        iLR = iLR * statA + l * r * (1 - statA); iLL = iLL * statA + l * l * (1 - statA); iRR = iRR * statA + r * r * (1 - statA);
        pkInL = juce::jmax (std::abs (l), pkInL * pkDecay); pkInR = juce::jmax (std::abs (r), pkInR * pkDecay);

        float M = 0.5f * (l + r), S = 0.5f * (l - r);

        // ---------------- GENERATE (side injection = mono-safe, plus Haas & room)
        const float a = smAmt.getNextValue();
        haasDelay.push (M); combDelay.push (M); chorusDelay.push (M);
        const float u = up.process (M, ratioUp), dn = down.process (M, ratioDn);
        float apOut = M; for (auto& f : ap) apOut = f.process (apOut);
        chorusPhase += chorusInc; if (chorusPhase >= 1) chorusPhase -= 1;
        float roomL = 0, roomR = 0;
        if (eRoom)
        {
            for (int k = 0; k < 4; ++k) roomL += roomCombs[(size_t) k].process (M);
            for (int k = 4; k < 8; ++k) roomR += roomCombs[(size_t) k].process (M);
            roomL = roomAp[1].process (roomAp[0].process (roomL * 0.25f));
            roomR = roomAp[3].process (roomAp[2].process (roomR * 0.25f));
        }
        if (genOn && a > 0.0001f)
        {
            float inj = 0;
            if (eDet)  inj += 0.7f * (u - dn);
            if (eCho)  inj += 0.6f * (chorusDelay.read ((0.007f + 0.004f * std::sin (twoPi * (float) chorusPhase)) * (float) sr) - M);
            if (eComb) inj += 0.7f * combDelay.read (timeS);
            if (eAp)   inj += 0.8f * apOut;
            S += a * inj;
            l = M + S; r = M - S;
            if (eHaas) r = r + a * (haasDelay.read (timeS) - M);
            if (eRoom) { l += a * 0.5f * roomL; r += a * 0.5f * roomR; }
            M = 0.5f * (l + r); S = 0.5f * (l - r);
        }

        // ---------------- SHAPE (multiband side width, bass mono, tilt, drive)
        if (shOn)
        {
            float b0, rest, b1, rest2, b2, b3;
            xo0.processSample (0, S, b0, rest);
            xo1.processSample (0, rest, b1, rest2);
            xo2.processSample (0, rest2, b2, b3);
            S = b0 * g[0] + b1 * g[1] + b2 * g[2] + b3 * g[3];
            if (drive > 0.001f)
            {
                float k = 1.0f + 6.0f * drive;
                S = S + drive * (std::tanh (S * k) / std::sqrt (k) - S);
            }
        }

        // ---------------- SPACE (shuffle, transient/sustain width, motion)
        if (spOn)
        {
            S += shuf * shuffleLp.lp (S);
            float am = std::abs (M);
            envFast = am > envFast ? am + (envFast - am) * atkF : am + (envFast - am) * relF;
            envSlow = am > envSlow ? am + (envSlow - am) * atkS : am + (envSlow - am) * relS;
            float trans = juce::jlimit (0.0f, 1.0f, (envFast - envSlow) / (envFast + 1e-6f) * 2.0f);
            S *= susW + (trW - susW) * trans;
            motionPhase += motionInc; if (motionPhase >= 1) motionPhase -= 1;
            if (depth > 0.001f) S += M * depth * 0.4f * std::sin (twoPi * (float) motionPhase);
        }

        // ---------------- GUARD (feed-forward correlation limiter on width)
        {
            float gl = M + S, gr = M - S;
            eLR = eLR * statA + gl * gr * (1 - statA); eLL = eLL * statA + gl * gl * (1 - statA); eRR = eRR * statA + gr * gr * (1 - statA);
            float corrPre = eLR / std::sqrt (eLL * eRR + 1e-12f);
            float target = 1.0f;
            if (gdOn && gAuto && eLL + eRR > 1e-8f && corrPre < thr)
                target = juce::jlimit (0.15f, 1.0f, 1.0f - (thr - corrPre) * 1.5f);
            float relMs = rec < 4 ? recMs[rec] : 300.0f + 1200.0f * juce::jlimit (0.0f, 1.0f, thr - corrPre);
            float relC = (float) std::exp (-1.0 / (relMs * 0.001 * sr));
            guardGain = target < guardGain ? target + (guardGain - target) * gAtk : target + (guardGain - target) * relC;
            if (gdOn && listen) { float rem = S * (1 - guardGain); M = 0; S = rem; }
            else if (gdOn) S *= guardGain;
        }

        // ---------------- OUTPUT
        M *= smMid.getNextValue(); S *= smSide.getNextValue();
        if (soloS && shOn) M = 0;
        if (soloM && shOn) S = 0;
        l = M + S; r = M - S;
        if (beyond && spOn)
        {
            beyondL.push (l); beyondR.push (r);
            float xd = 0.00027f * (float) sr;
            l -= 0.35f * beyondLpR.lp (beyondR.read (xd));
            r -= 0.35f * beyondLpL.lp (beyondL.read (xd));
        }
        const float mix = smMix.getNextValue(), og = smGain.getNextValue();
        l = (dryL + (l - dryL) * mix) * og;
        r = (dryR + (r - dryR) * mix) * og;
        if (monoOut) { float m = 0.5f * (l + r); l = r = m; }
        if (bypass) { l = dryL; r = dryR; }
        L[i] = l; R[i] = r;

        // meters
        oLR = oLR * statA + l * r * (1 - statA); oLL = oLL * statA + l * l * (1 - statA); oRR = oRR * statA + r * r * (1 - statA);
        pkOutL = juce::jmax (std::abs (l), pkOutL * pkDecay); pkOutR = juce::jmax (std::abs (r), pkOutR * pkDecay);
        float mm = 0.5f * (l + r), ss = 0.5f * (l - r);
        rmsM = rmsM * statA + mm * mm * (1 - statA); rmsS = rmsS * statA + ss * ss * (1 - statA);
        if (++scopeDecim >= 2)
        {
            scopeDecim = 0;
            int w = scopeWrite.load (std::memory_order_relaxed);
            scope[(size_t) (w * 2)] = l; scope[(size_t) (w * 2 + 1)] = r;
            scopeWrite.store ((w + 1) % scopeSize, std::memory_order_release);
        }
    }

    mInL = pkInL; mInR = pkInR; mOutL = pkOutL; mOutR = pkOutR;
    mMid = std::sqrt (rmsM); mSide = std::sqrt (rmsS);
    mCorr = (oLL + oRR > 1e-9f) ? oLR / std::sqrt (oLL * oRR + 1e-12f) : 1.0f;
    mInCorr = (iLL + iRR > 1e-9f) ? iLR / std::sqrt (iLL * iRR + 1e-12f) : 1.0f;
    mPull = 1.0f - guardGain;
}

void SpreadProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    auto st = apvts.copyState();
    st.setProperty ("uiScale", uiScale, nullptr);
    if (auto xml = st.createXml()) copyXmlToBinary (*xml, destData);
}

void SpreadProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    if (auto xml = getXmlFromBinary (data, sizeInBytes))
        if (xml->hasTagName (apvts.state.getType()))
        {
            auto tree = juce::ValueTree::fromXml (*xml);
            uiScale = (double) tree.getProperty ("uiScale", 0.8);
            apvts.replaceState (tree);
        }
}

juce::AudioProcessorEditor* SpreadProcessor::createEditor() { return new SpreadEditor (*this); }

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new SpreadProcessor(); }
