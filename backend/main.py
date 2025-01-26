from analysis.patient_notifications import patient_notifications
from analysis.priority_list import priority_patient_list
from analysis.population_insights import population_insights
from analysis.temporal_analysis import temporal_analysis
from analysis.alert_escalation import alert_escalation
from logger import setup_logger

# Set up logger
logger = setup_logger(name="analysis_runner", log_file="analysis_runner.log")

if __name__ == "__main__":
    logger.info("Starting Analysis Pipeline")

    try:
        logger.info("Executing Patient-Level Notifications")
        patient_notifications()
        logger.info("Patient-Level Notifications completed successfully")
    except Exception as e:
        logger.error(f"Error in Patient-Level Notifications: {e}")

    try:
        logger.info("Executing Priority Patient List")
        priority_patient_list()
        logger.info("Priority Patient List completed successfully")
    except Exception as e:
        logger.error(f"Error in Priority Patient List: {e}")

    try:
        logger.info("Executing Population-Level Insights")
        population_insights()
        logger.info("Population-Level Insights completed successfully")
    except Exception as e:
        logger.error(f"Error in Population-Level Insights: {e}")

    try:
        logger.info("Executing Temporal Analysis")
        temporal_analysis()
        logger.info("Temporal Analysis completed successfully")
    except Exception as e:
        logger.error(f"Error in Temporal Analysis: {e}")

    try:
        logger.info("Executing Alert Escalation System")
        alert_escalation()
        logger.info("Alert Escalation System completed successfully")
    except Exception as e:
        logger.error(f"Error in Alert Escalation System: {e}")

    logger.info("Analysis Pipeline Completed")
