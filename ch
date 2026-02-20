func (h *handlers) checkMaintenanceEventsCore(projectID string, zone string, clusterName string) (string, error) {
	genericCore.WriteToLog("-------------------checkMaintenanceEventsCore()-------------------")

	nodeList, success := getComputeNodesInCluster(clusterName+"-login-001", zone, projectID)
	if !success {
		return fmt.Sprintf("Could not get nodes in cluster %s in project %s", clusterName, projectID), nil
	}

	ctx := context.Background()
	computeService, err := compute.NewService(ctx)
	if err != nil {
		return fmt.Sprintf("Failed to create compute service: %v", err), nil
	}

	returnStr := ""

	for _, node := range nodeList {
		instance, err := computeService.Instances.Get(projectID, zone, node).Do()
		returnStr += "Maintenance info for node " + node + " : "

		if err != nil {
			returnStr += fmt.Sprintf("Could not get maintenance info: %v\n", err)
			continue
		}

		// Native scheduling inspection
		if instance.Scheduling != nil && instance.Scheduling.OnHostMaintenance != "" {
			returnStr += fmt.Sprintf("OnHostMaintenance: %s\n", instance.Scheduling.OnHostMaintenance)
		}

		if instance.Scheduling != nil && instance.Scheduling.Preemptible {
			returnStr += "Preemptible: true\n"
		}

		if instance.Status != "" {
			returnStr += fmt.Sprintf("Instance Status: %s\n", instance.Status)
		}

		if instance.Scheduling == nil {
			returnStr += "No scheduling info available\n"
		}

		returnStr += "\n"
	}

	return returnStr, nil
}
