from sqlalchemy import text


def seed_metrics(connection):
    """
    Seed initial 2024 annual report metrics for Apple, Microsoft, and Tesla.
    """
    seed_records = [
        {
            "company": "Apple",
            "year": "2024",
            "revenue": "$391,035",
            "net_income": "$93,736",
            "operating_income": "$123,216",
            "cash_flow": "$118,254",
            "total_assets": "$364,980",
            "total_liabilities": "$308,030",
            "risk_factors": (
                "Macroeconomic conditions including inflation, interest rates, and currency fluctuations could materially impact consumer spending.\n"
                "Intense global competition with aggressive pricing, short product life cycles, and rapid technological transitions.\n"
                "Dependence on single or limited-source suppliers for key components, creating exposure to supply disruptions.\n"
                "Exposure to foreign exchange rate fluctuations affecting international sales, margins, and financial results.\n"
                "Complex global regulatory, antitrust, and tax investigations, including European State Aid compliance."
            ),
            "growth_drivers": (
                "Record expansion in Services revenue fueled by Cloud, App Store, Apple Pay, and subscription platforms.\n"
                "Strong global demand for iPhone 16 series powered by Apple Intelligence on-device AI architecture.\n"
                "Mac ecosystem momentum driven by next-generation M-series Apple Silicon performance and efficiency.\n"
                "Active installed device base surpassing 2.2 billion active devices worldwide.\n"
                "Disciplined capital allocation including continuous share repurchase and dividend return programs."
            )
        },
        {
            "company": "Microsoft",
            "year": "2024",
            "revenue": "$245,122",
            "net_income": "$88,136",
            "operating_income": "$109,433",
            "cash_flow": "$118,548",
            "total_assets": "$512,163",
            "total_liabilities": "$243,686",
            "growth_drivers": (
                "Exceptional growth across Microsoft Cloud and Azure OpenAI enterprise infrastructure adoption.\n"
                "Rapid enterprise monetization of Microsoft 365 Copilot and GitHub Copilot developer platforms.\n"
                "Expansion of Server products and cloud services revenue driven by hybrid cloud demand.\n"
                "Integration of Activision Blizzard significantly expanding gaming and Xbox content monetization.\n"
                "Strong commercial cloud gross margin expansion supported by efficiency in hyperscale datacenter operations."
            ),
            "risk_factors": (
                "Substantial capital expenditures required to expand global datacenter and AI computing infrastructure.\n"
                "Evolving global regulations and legal scrutiny surrounding artificial intelligence and algorithmic accountability.\n"
                "Cybersecurity threats and sophisticated attacks targeting cloud platforms and enterprise software services.\n"
                "Fierce cloud hyperscaler competition from Amazon AWS and Google Cloud Platform in AI infrastructure.\n"
                "Geopolitical restrictions on international technology transfers and semiconductor availability."
            )
        },
        {
            "company": "Tesla",
            "year": "2024",
            "revenue": "$97,690",
            "net_income": "$7,088",
            "operating_income": "$7,077",
            "cash_flow": "$13,256",
            "total_assets": "$114,841",
            "total_liabilities": "$46,478",
            "growth_drivers": (
                "Massive expansion in Tesla Energy segment with record Megapack and Powerwall deployment volume.\n"
                "Continued vehicle delivery leadership of Model Y as the world's best-selling passenger vehicle.\n"
                "Rapid technological advancements in Full Self-Driving (Supervised) neural networks and Dojo AI clusters.\n"
                "Ongoing development of next-generation affordable vehicle platform and Cybercab autonomous fleet.\n"
                "Global adoption of the North American Charging Standard (NACS) and Supercharger network licensing."
            ),
            "risk_factors": (
                "Intensifying pricing pressure and competition across global electric vehicle markets, notably in China.\n"
                "Technological and regulatory uncertainty regarding autonomous vehicle validation and commercial robotaxi operation.\n"
                "Volatility in critical battery raw material costs including lithium, nickel, and cobalt.\n"
                "Production scaling challenges for new architectures such as Cybertruck and 4680 battery cells.\n"
                "Key-person dependency on executive leadership and brand reputation sensitivity."
            )
        }
    ]

    insert_query = """
    INSERT INTO financial_metrics (
        company, year, revenue, net_income, operating_income,
        cash_flow, total_assets, total_liabilities, risk_factors, growth_drivers
    ) VALUES (
        :company, :year, :revenue, :net_income, :operating_income,
        :cash_flow, :total_assets, :total_liabilities, :risk_factors, :growth_drivers
    )
    """

    for record in seed_records:
        connection.execute(text(insert_query), record)
    
    print("Pre-seeded financial metrics for Apple, Microsoft, and Tesla successfully.")
