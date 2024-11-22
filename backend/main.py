from analysis.patient_notifications import patient_notifications
from analysis.priority_list import priority_patient_list
from analysis.population_insights import population_insights
from analysis.temporal_analysis import temporal_analysis
from analysis.alert_escalation import alert_escalation

if __name__ == "__main__":
    print("\n--- Patient-Level Notifications ---")
    patient_notifications("Xsu5hUsKlrQnAWLcH+UnKA==")

    print("\n--- Priority Patient List ---")
    priority_patient_list()

    print("\n--- Population-Level Insights ---")
    population_insights()

    print("\n--- Temporal Analysis ---")
    temporal_analysis()

    print("\n--- Alert Escalation System ---")
    alert_escalation()
