let eventTypesChart, activityChart;
let websocket = null;
let isConnected = false;

// WebSocket connection
function connectWebSocket() {
	const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
	const wsUrl = `${protocol}//${window.location.host}/ws`;

	websocket = new WebSocket(wsUrl);

	websocket.onopen = function (event) {
		console.log("WebSocket connected");
		isConnected = true;
		updateConnectionStatus(true);
	};

	websocket.onmessage = function (event) {
		const data = JSON.parse(event.data);
		handleWebSocketMessage(data);
	};

	websocket.onclose = function (event) {
		console.log("WebSocket disconnected");
		isConnected = false;
		updateConnectionStatus(false);

		// Try to reconnect after 3 seconds
		setTimeout(connectWebSocket, 3000);
	};

	websocket.onerror = function (error) {
		console.error("WebSocket error:", error);
	};
}

function handleWebSocketMessage(data) {
	switch (data.type) {
		case "initial_data":
			updateStats(data.stats);
			updateEventsTable(data.events);
			updateCharts(data.stats.event_types, data.events);
			updateFunnel(data.funnel);
			updateSegmentation(data.segmentation);
			break;

		case "new_event":
			// Add the new event to the table (prepend to top)
			addEventToTable(data.data);
			showEventNotification(data.data);
			break;

		case "stats_update":
			updateStats(data.data);
			// Refresh charts with new data
			loadFullData();
			break;

		case "funnel_update":
			updateFunnel(data.data);
			break;

		case "segmentation_update":
			updateSegmentation(data.data);
			break;
	}
}

function updateConnectionStatus(connected) {
	const statusElement = document.getElementById("connectionStatus");
	if (!statusElement) {
		// Create status indicator if it doesn't exist
		const header = document.querySelector(".header");
		const statusDiv = document.createElement("div");
		statusDiv.id = "connectionStatus";
		statusDiv.style.cssText =
			"margin-top: 10px; padding: 5px 10px; border-radius: 4px; font-size: 0.9em;";
		header.appendChild(statusDiv);
	}

	const statusEl = document.getElementById("connectionStatus");
	if (connected) {
		statusEl.textContent = "🟢 Live Updates Active";
		statusEl.style.backgroundColor = "#dcfce7";
		statusEl.style.color = "#166534";
	} else {
		statusEl.textContent = "🔴 Connecting...";
		statusEl.style.backgroundColor = "#fee2e2";
		statusEl.style.color = "#dc2626";
	}
}

function addEventToTable(eventData) {
	const tbody = document.getElementById("eventsTableBody");

	// Create new row
	const row = tbody.insertRow(0); // Insert at top
	row.style.backgroundColor = "#f0f9ff"; // Highlight new events

	row.innerHTML = `
        <td>#${eventData.id}</td>
        <td><span class="event-type event-${eventData.event_type}">${
		eventData.event_type
	}</span></td>
        <td>${eventData.user_id || "Anonymous"}</td>
        <td>${JSON.stringify(eventData.data).substring(0, 100)}...</td>
        <td>${eventData.timestamp}</td>
    `;

	// Remove highlight after 3 seconds
	setTimeout(() => {
		row.style.backgroundColor = "";
	}, 3000);

	// Keep only the latest 20 rows
	while (tbody.rows.length > 20) {
		tbody.deleteRow(tbody.rows.length - 1);
	}
}

function showEventNotification(eventData) {
	// Create a simple notification
	const notification = document.createElement("div");
	notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #3b82f6;
        color: white;
        padding: 10px 15px;
        border-radius: 4px;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

	// Add CSS animation
	if (!document.getElementById("notificationStyles")) {
		const style = document.createElement("style");
		style.id = "notificationStyles";
		style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
		document.head.appendChild(style);
	}

	notification.textContent = `New ${eventData.event_type} event`;
	document.body.appendChild(notification);

	// Remove notification after 3 seconds
	setTimeout(() => {
		notification.remove();
	}, 3000);
}

async function loadFullData() {
	// Load full data for charts (WebSocket only sends partial updates)
	try {
		const [statsResponse, eventsResponse] = await Promise.all([
			fetch("/stats"),
			fetch("/events?limit=20"),
		]);

		const stats = await statsResponse.json();
		const eventsData = await eventsResponse.json();

		updateCharts(stats.event_types, eventsData.events);
	} catch (error) {
		console.error("Error loading full data:", error);
	}
}

function updateStats(stats) {
	document.getElementById("totalEvents").textContent = stats.total_events;
	document.getElementById("uniqueUsers").textContent = stats.unique_users;
	document.getElementById("recentEvents").textContent =
		stats.events_last_hour;
	document.getElementById("eventTypes").textContent = Object.keys(
		stats.event_types
	).length;
}

function updateEventsTable(events) {
	const tbody = document.getElementById("eventsTableBody");
	tbody.innerHTML = "";

	events.forEach((event) => {
		const row = tbody.insertRow();
		row.innerHTML = `
            <td>#${event.id}</td>
            <td><span class="event-type event-${event.event_type}">${
			event.event_type
		}</span></td>
            <td>${event.user_id || "Anonymous"}</td>
            <td>${JSON.stringify(event.data).substring(0, 100)}...</td>
            <td>${new Date(event.created_at).toLocaleTimeString()}</td>
        `;
	});
}

function updateCharts(eventTypes, events) {
	// Event Types Chart
	if (eventTypesChart) eventTypesChart.destroy();

	const ctx1 = document.getElementById("eventTypesChart").getContext("2d");
	eventTypesChart = new Chart(ctx1, {
		type: "doughnut",
		data: {
			labels: Object.keys(eventTypes),
			datasets: [
				{
					data: Object.values(eventTypes),
					backgroundColor: [
						"#3b82f6",
						"#10b981",
						"#f59e0b",
						"#ef4444",
						"#8b5cf6",
						"#06b6d4",
					],
				},
			],
		},
		options: {
			responsive: true,
			plugins: { legend: { position: "bottom" } },
		},
	});

	// Activity Chart
	if (activityChart) activityChart.destroy();

	const hourCounts = {};
	events.forEach((event) => {
		const hour = new Date(event.created_at).getHours();
		hourCounts[hour] = (hourCounts[hour] || 0) + 1;
	});

	const ctx2 = document.getElementById("activityChart").getContext("2d");
	activityChart = new Chart(ctx2, {
		type: "line",
		data: {
			labels: Object.keys(hourCounts).sort(),
			datasets: [
				{
					label: "Events per Hour",
					data: Object.keys(hourCounts)
						.sort()
						.map((h) => hourCounts[h]),
					borderColor: "#3b82f6",
					backgroundColor: "rgba(59, 130, 246, 0.1)",
					tension: 0.4,
				},
			],
		},
		options: {
			responsive: true,
			scales: { y: { beginAtZero: true } },
		},
	});
}

async function sendTestEvent(eventType, data) {
	try {
		const response = await fetch("/track", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				event_type: eventType,
				user_id: "test_user_" + Math.floor(Math.random() * 100),
				data: data,
			}),
		});

		if (response.ok) {
			// No need to manually refresh - WebSocket will handle it!
			console.log("Event sent successfully");
		}
	} catch (error) {
		console.error("Error sending test event:", error);
	}
}

// New function to generate demo traffic
async function generateDemoTraffic() {
	try {
		const response = await fetch("/demo/generate-traffic", {
			method: "POST",
		});

		if (response.ok) {
			console.log("Demo traffic generated");
		}
	} catch (error) {
		console.error("Error generating demo traffic:", error);
	}
}

function updateFunnel(funnelData) {
	const counts = funnelData.funnel_counts;
	const rates = funnelData.conversion_rates;

	// Update counts
	document.getElementById("funnelPageView").textContent = counts.page_view;
	document.getElementById("funnelProductView").textContent =
		counts.product_view;
	document.getElementById("funnelAddToCart").textContent = counts.add_to_cart;
	document.getElementById("funnelSignup").textContent = counts.user_signup;
	document.getElementById("funnelPurchase").textContent = counts.purchase;

	// Update conversion rates
	document.getElementById("funnelPageViewRate").textContent =
		rates.page_view + "%";
	document.getElementById("funnelProductViewRate").textContent =
		rates.product_view + "%";
	document.getElementById("funnelAddToCartRate").textContent =
		rates.add_to_cart + "%";
	document.getElementById("funnelSignupRate").textContent =
		rates.user_signup + "%";
	document.getElementById("funnelPurchaseRate").textContent =
		rates.purchase + "%";
}

function updateSegmentation(segmentationData) {
	document.getElementById("segmentConverted").textContent =
		segmentationData.converted.length;
	document.getElementById("segmentHighIntent").textContent =
		segmentationData.high_intent.length;
	document.getElementById("segmentMediumIntent").textContent =
		segmentationData.medium_intent.length;
	document.getElementById("segmentLowIntent").textContent =
		segmentationData.low_intent.length;
}

// Manual refresh function (keep for backup)
async function loadData() {
	if (!isConnected) {
		// Fallback to manual loading if WebSocket is not connected
		await loadFullData();
	}
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", function () {
	// Connect WebSocket for real-time updates
	connectWebSocket();

	// Fallback: load data manually if WebSocket fails
	setTimeout(() => {
		if (!isConnected) {
			loadData();
		}
	}, 2000);
});
