from typing import Dict, Tuple


def _key(case_name: str, variant_name: str, temperature: float) -> Tuple[str, str, float]:
    return case_name.lower(), variant_name.lower(), float(temperature)


_RESPONSES: Dict[Tuple[str, str, float], str] = {
    _key("linkedin_b2b_saas", "Direct & minimal", 0.2): (
        "Last quarter I realised my forecast updates were always late.\n\n"
        "I kept three different spreadsheets open, each telling a slightly different story. It was embarrassing to walk into a leadership meeting knowing the number might shift after the call.\n\n"
        "So I forced myself to clean up the way I tracked pipeline and risk. One simple change was keeping one view that everyone agreed on, even if it wasn’t perfect.\n\n"
        "Since then I sleep better before forecast reviews. I’m more interested in the conversations that follow the number than defending the number itself.\n\n"
        "Curious how others handle that moment when you realise your reporting stack is more complex than the decisions you’re trying to make."
    ),
    _key("linkedin_b2b_saas", "Direct & minimal", 0.7): (
        "I used to treat revenue forecasts like an exam.\n\n"
        "I would disappear for a day, wrestle with exports, and then present a single perfect number. The problem was that no one trusted it, including me.\n\n"
        "What helped wasn’t a new tool, it was changing the conversation. I started sharing the assumptions, the messy parts of the pipeline, and the trade-offs we were making.\n\n"
        "Leaders stopped asking “Is this number right?” and started asking “What would it take to shift this scenario?”. That felt like progress.\n\n"
        "How do you make your forecast reviews feel more like a conversation than a test?"
    ),
    _key("linkedin_b2b_saas", "Direct & minimal", 1.0): (
        "Tired of messy revenue forecasts and clunky spreadsheets? Our cutting-edge platform is a total game-changer that will unlock your pipeline, supercharge your team, and drive predictable growth in minutes!!!\n\n"
        "We seamlessly connect every data source across your GTM motion so you can crush your number every quarter with next-level visibility.\n\n"
        "Ready to transform your forecast and boost your results? Book a demo today and see how our revolutionary solution can take your revenue engine to the next level."
    ),
    _key("linkedin_b2b_saas", "Problem -> Solution -> Proof", 0.2): (
        "A few years ago I walked into a board meeting with three different forecast numbers.\n\n"
        "Sales had one, finance had another, and I had my own “best guess” based on late-night spreadsheet surgery. Everyone knew it, and the conversation never really recovered.\n\n"
        "Since then I’ve become almost stubborn about having one simple, shared view of revenue. It’s not perfect, but it’s honest. When something changes, we talk about why instead of pretending the spreadsheet was right all along.\n\n"
        "The funny thing is that trust went up before accuracy did. Once people believed the process, they were willing to help improve it.\n\n"
        "Have you had a moment where your forecast process clearly needed to grow up?"
    ),
    _key("linkedin_b2b_saas", "Problem -> Solution -> Proof", 0.7): (
        "The most awkward forecast review I’ve ever led started with a simple question: “Why does finance show a different number than sales?”\n\n"
        "We weren’t missing tools. We were missing a shared story about the pipeline. Sales cared about momentum, finance cared about risk, and leadership just wanted to know if the plan still made sense.\n\n"
        "What finally helped was sitting down with both teams and rebuilding the view from scratch: one set of stages, one definition of risk, one way to talk about upside.\n\n"
        "Since then, the reviews are still tense sometimes, but at least we argue about the same reality.\n\n"
        "If you’ve been through a similar reset, what did you change first?"
    ),
    _key("linkedin_b2b_saas", "Problem -> Solution -> Proof", 1.0): (
        "Imagine a world where your revenue forecast is always 98% accurate, your churn drops by 63% in the first month, and every rep magically updates the CRM on time.\n\n"
        "That’s what our next-level platform delivers for forward-thinking SaaS leaders around the globe. Customers routinely see 4x pipeline velocity and 200% ROI in under 30 days.\n\n"
        "Stop guessing and start winning. Our seamless solution gives you one source of truth, predictive insights, and the power to crush your targets every single quarter.\n\n"
        "Ready to unlock this kind of performance? Book a demo and see the numbers for yourself."
    ),
    _key("linkedin_b2b_saas", "Objection-handling", 0.2): (
        "\"We already have dashboards\" is the line I hear most often.\n\n"
        "I get it. I used to think the same. For a while I hid behind screenshots instead of admitting that I didn’t really trust the underlying data.\n\n"
        "What changed for me wasn’t a new dashboard, it was getting honest about what the board actually needed: a story about risk, not just a chart.\n\n"
        "Now, when someone shows me a beautiful report, my first question is, “What would have to be true for this to be wrong?”\n\n"
        "How do you push past the comfort of dashboards and get to the real conversation?"
    ),
    _key("linkedin_b2b_saas", "Objection-handling", 0.7): (
        "\"Our sales team won’t adopt another process\" is usually a polite way of saying “we’ve burned them before”.\n\n"
        "When I first tried to tighten up our forecast hygiene, I pushed a new template and weekly ritual on the team. They played along for a month and then quietly went back to old habits.\n\n"
        "The second time, I started with their reality instead of mine: what they hated about the current process, what actually helped them close deals, and what we could remove instead of add.\n\n"
        "The end result looked less “designed” than my original idea, but adoption went up because it felt like theirs.\n\n"
        "If you’ve successfully changed a sales habit, what made it stick?"
    ),
    _key("linkedin_b2b_saas", "Objection-handling", 1.0): (
        "\"We’re different\" is what every next-level, cutting-edge SaaS company says before they discover our game-changing platform.\n\n"
        "Our seamless, all-in-one solution is built to unlock hidden revenue, supercharge your pipeline, and boost your results without any extra effort from your team.\n\n"
        "No more manual work, no more messy data, just predictable growth on autopilot.\n\n"
        "If you’re ready to transform your revenue engine and crush your targets, book a demo today and see how we can take your business to the next level."
    ),
}


def generate_dryrun(case_name: str, variant_name: str, temperature: float) -> str:
    key = _key(case_name, variant_name, temperature)
    return _RESPONSES.get(
        key,
        "Mock output for case={case_name}, variant={variant_name}, temperature={temperature}.".format(
            case_name=case_name, variant_name=variant_name, temperature=temperature
        ),
    )
