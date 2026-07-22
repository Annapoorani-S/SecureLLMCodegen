"""
AISAF Security Score Engine

Calculates security score based on
Bandit and Semgrep findings.
"""


def calculate_security_score(report):

    """
    Input:
        Scanner report

    Output:
        Security score (0-100)
    """


    score = 100


    issues = report.get(
        "issues",
        []
    )


    for issue in issues:


        severity = issue.get(
            "severity",
            "LOW"
        ).upper()



        if severity == "HIGH":

            score -= 20



        elif severity == "MEDIUM":

            score -= 10



        elif severity == "LOW":

            score -= 5



        elif severity == "INFO":

            score -= 1



    if score < 0:

        score = 0



    return score





def security_status(score):


    if score >= 90:

        return "SECURE"


    elif score >= 70:

        return "MODERATE RISK"


    else:

        return "HIGH RISK"