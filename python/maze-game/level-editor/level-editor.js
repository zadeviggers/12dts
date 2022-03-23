"use-strict";

const gameSettings = [
	["title", "string"],
	["width", "number"],
	["height", "number"],
	["background_colour", "colour"],
	["player_colour", "colour"],
	["drag", "number"],
	["player_height", "number"],
	["player_width", "number"],
	["player_walk_speed", "number"],
	["player_max_speed", "number"],
];
// Game data will be stored here when generated
let gameData = null;
// Keep track of created elements so that they can be deleted later
let createdElements = [];

// Get elements
const saveButton = document.getElementById("save-button");
const gameSettingsForm = document.getElementById("game-settings-form");
const gameFileInput = document.getElementById("game-file-input");

// Event listeners
saveButton.addEventListener("click", (event) => {
	// Use tabs for indenting JSON
	const stringified = JSON.stringify(gameData, null, "	");
	const file = new Blob([stringified], { type: "application/json" });
	// The following code is based on a portion of the code in this answer: https://stackoverflow.com/a/30832210
	const downloadAnchor = document.createElement("a");
	const url = URL.createObjectURL(file);
	downloadAnchor.href = url;
	downloadAnchor.download = "game-data.json";
	document.body.appendChild(downloadAnchor);
	downloadAnchor.click();
	setTimeout(function () {
		document.body.removeChild(downloadAnchor);
		window.URL.revokeObjectURL(url);
	}, 0);
});
gameFileInput.addEventListener("change", (event) => {
	const file = gameFileInput.files[0];
	const fileReader = new FileReader();

	fileReader.addEventListener("load", () => {
		try {
			gameData = JSON.parse(fileReader.result);
			onDataLoaded();
		} catch (error) {
			alert("Error parsing file: " + error);
		}
	});

	fileReader.addEventListener("error", () => {
		alert("Error decoding file: " + fileReader.error);
	});

	fileReader.readAsText(file);
});

// Functions
function onDataLoaded() {
	removeAllCreatedElements();
	for (const [key, type] of gameSettings) {
		const inputElement = document.createElement("input");
		inputElement.setAttribute("id", key);
		inputElement.setAttribute("name", key);
		inputElement.setAttribute("value", gameData[key]);
		if (type === "string") {
			inputElement.setAttribute("type", "text");
		} else if (type === "number") {
			inputElement.setAttribute("type", "number");
		} else if (type === "colour") {
			inputElement.setAttribute("type", "color");
			// Colour input elements use hex values
			inputElement.setAttribute(
				"value",
				rgbToHex(gameData[key][0], gameData[key][1], gameData[key][2])
			);
		}

		inputElement.addEventListener("change", onGameSettingInputChange);

		const labelElement = document.createElement("label");
		labelElement.textContent = key;
		labelElement.setAttribute("for", key);
		labelElement.appendChild(inputElement);
		gameSettingsForm.appendChild(labelElement);

		createdElements.push(inputElement, labelElement);
	}
}

function removeAllCreatedElements() {
	for (const element of createdElements) {
		element.remove();
	}
}

function onGameSettingInputChange(event) {
	const element = event.target;
	const type = element.getAttribute("type");
	if (type === "text") {
		gameData[element.id] = element.value;
	} else if (type === "number") {
		gameData[element.id] = Number(element.value);
	} else if (type === "color") {
		gameData[element.id] = hexToRgb(element.value);
	}
}

// These functiuons are from this answer: https://stackoverflow.com/a/5624139
function rgbToHex(r, g, b) {
	function componentToHex(c) {
		const hex = c.toString(16);
		return hex.length == 1 ? "0" + hex : hex;
	}
	return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}
function hexToRgb(hex) {
	const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
	return result
		? [
				parseInt(result[1], 16),
				parseInt(result[2], 16),
				parseInt(result[3], 16),
		  ]
		: null;
}
