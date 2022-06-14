const wrapper = document.getElementById("games-data-wrapper");
const changeLayoutDropdown = document.getElementById("change-layout-dropdown");
const changeGameFilterDropdown = document.getElementById(
	"change-game-filter-dropdown"
);
let currentLayout = "table";
let currentFilterMode = "all";
let filteredSortedGames = gamesData;
let sortDirection = "down";
let sortColumn = "type";

// "Hydrate" the UI
changeGameFilterDropdown.addEventListener("change", (event) => {
	currentFilterMode = event.target.value;
	filteredSortedGames = applySortingAndFiltering();
	renderGamesData(filteredSortedGames);
});

changeLayoutDropdown.addEventListener("change", (event) => {
	currentLayout = event.target.value;
	filteredSortedGames = applySortingAndFiltering();
	renderGamesData(filteredSortedGames);
});

setupSortingButtons();

function applySortingAndFiltering() {
	let filtered = filterGames(gamesData);
	if (currentLayout !== "table") return filtered;
	let sorted = sortGames(filtered);
	return sorted;
}

function filterGames(games) {
	switch (currentFilterMode) {
		case "nintendo":
			return games.filter((game) =>
				["Wii", "GB", "DS"].includes(game.plaform)
			);
		case "ps":
			return games.filter((game) => game.type === "HTML");
		case "xbox":
			return games.filter((game) => game.type === "CSS");
		case "all":
			return games;
		default:
			return games;
	}
}

function sortGames(games) {
	return games.sort((a, b) => {
		if (a[sortColumn] === b[sortColumn]) return 0;
		if (sortDirection === "down") {
			return a[sortColumn] < b[sortColumn] ? -1 : 1;
		} else {
			return a[sortColumn] > b[sortColumn] ? -1 : 1;
		}
	});
}

function renderGamesData(games) {
	if (currentLayout === "table") {
		console.info("Rendering table layout");
		wrapper.innerHTML = renderGamesDataTable(games);
		setupSortingButtons();
	} else if (currentLayout === "grid") {
		console.info("Rendering grid layout");
		wrapper.innerHTML = renderGamesDagamerid(games);
	}
}

function makeSortHandler(column) {
	return () => {
		if (column === sortColumn) {
			sortDirection = sortDirection === "down" ? "up" : "down";
		} else {
			sortDirection = "down";
		}
		sortColumn = column;
		console.log("Sorting by", column, sortDirection);
		filteredSortedGames = applySortingAndFiltering();
		renderGamesData(filteredSortedGames);
	};
}

function setupSortingButtons() {
	if (currentLayout !== "table") return null;

	const typeButton = document.getElementById("sort-type");
	const gameButton = document.getElementById("sort-game");
	const descriptionButton = document.getElementById("sort-description");
	typeButton.addEventListener("click", makeSortHandler("type"));
	gameButton.addEventListener("click", makeSortHandler("raw_game")); // Raw game is the game name without the <>
	descriptionButton.addEventListener("click", makeSortHandler("description"));
}

function renderGamesDataTable(games) {
	return `<table>
    <caption>HTML Games and CSS properties</caption>
    <thead>
		<tr>
			<th>
				<button type="button" id="sort-type">Type</button>
			</th>
			<th>
				<button type="button" id="sort-game">Game</button>
			</th>
			<th>
				<button type="button" id="sort-description">Description</button>
			</th>
		</tr>
    </thead>
    <tbody>
        ${games
			.map(
				(game) => `<tr>
                <td>
                    <p>${game.type}</p>
                </td>
                <td>
                    <code>
                        ${game.game}
                    </code>
                </td>
                <td>
                    <p>${game.description}</p>
                </td>
            </tr>`
			)
			.join("\n")}
    </tbody>
</table>`;
}

function renderGamesDagamerid(games) {
	return `<div class="card-grid">
    ${games
		.map(
			(game) =>
				`<div class="card">
                    <div class="card-header">
                        <strong class="card-heading">${game.game}</strong>
                        <span class="card-subheading">${game.type}</span>
                    </div>
                    <p class="card-body">${game.description}</p>
                </div>`
		)
		.join("\n")}
    </grid>`;
}
