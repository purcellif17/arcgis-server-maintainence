#pylint: disable=E1101

import os.path
import arcpy
import logging

# Point to SDE Connection
arcpy.env.workspace = ""
SDE = arcpy.env.workspace

# Set up logger in current folder.
file_loc = os.path.dirname(__file__)
logging.basicConfig(filename='server_maintenance.log',filemode='w',format='%(asctime)s | %(lineno)s | %(levelname)s | %(message)s',level=logging.INFO)

# Reconcile all versions and compress database
try:
    logging.debug('Disconnecting users')
    # Stop connections
    arcpy.AcceptConnections(SDE, False)
    # Disconnect users
    arcpy.DisconnectUser(SDE, "ALL")

    # Get version list
    version_list = arcpy.ListVersions(SDE)
    logging.info('Reconciling versions...')
    # Reconcile edits
    arcpy.ReconcileVersions_management(SDE,
                                       reconcile_mode="ALL_VERSIONS",
                                       target_version="dbo.DEFAULT",
                                       edit_versions=version_list,
                                       acquire_locks="LOCK_AQUIRED",
                                       abort_if_conflicts="NO_ABORT",
                                       conflict_definition="BY_OBJECT",
                                       conflict_resolution="FAVOR_TARGET_VERSION",
                                       with_post="POST",
                                       with_delete="DELETE_VERSION",
                                       out_log=os.path.join(file_loc,'reconcile_log')
                                       )
    # Compress database and reopen to outside connections
    logging.info('Compressing database...')
    arcpy.Compress_management(SDE)
    arcpy.AcceptConnections(SDE, True)
    logging.debug('Open to connections')
except:
    print("There was an error!")
    logging.error("An error has occured while reconciling and compressing versions",exc_info=True)
    arcpy.AcceptConnections(SDE, True)

# Rebuild indexes and update statistics
try:
    logging.info("Rebuilding indexes...")
    arcpy.RebuildIndexes_management(SDE,"SYSTEM")
    logging.info("Updating statistics")
    arcpy.AnalyzeDatasets_management(SDE,"SYSTEM")
except:
    logging.error("An error has occured while rebuilding indexes and updating statistics.",exc_info=True)

logging.info("SCRIPT COMPLETE")