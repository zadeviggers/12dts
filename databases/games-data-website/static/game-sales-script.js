const wrapper = document.getElementById("games-data-wrapper");
const changeLayoutDropdown = document.getElementById("change-layout-dropdown");
const changeGameFilterDropdown = document.getElementById(
	"change-game-filter-dropdown"
);
const searchParams = new URLSearchParams(location.search);
const searchText = searchParams.get("search-text");
let currentLayout = "table";
let currentFilterMode = searchParams.get("brand") || "all";
let filteredSortedGames = gamesData;
let sortDirection = "down";
let sortColumn = "type";

// "Hydrate" the UI
changeGameFilterDropdown.value = currentFilterMode;
changeGameFilterDropdown.addEventListener("change", (event) => {
	currentFilterMode = event.target.value;
	const pushStateSearchParams = new URLSearchParams();
	pushStateSearchParams.set("brand", currentFilterMode);
	if (searchText) pushStateSearchParams.set("search-text", searchText);
	history.pushState(
		{},
		null,
		`/game-sales${"?" + pushStateSearchParams.toString()}`
	);
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
	console.info(`Filtering to platofrm: ${currentFilterMode}`);

	switch (currentFilterMode) {
		case "pc":
			return games.filter((game) => game.Platform === "PC");
		case "atari":
			return games.filter((game) => game.Platform === "2600");
		case "nintendo":
			return games.filter((game) =>
				[
					"Wii",
					"GB",
					"DS",
					"N64",
					"NES",
					"SNES",
					"GBA",
					"3DS",
					"GC",
					"WiiU",
				].includes(game.Platform)
			);

		case "ps":
			return games.filter((game) =>
				["PS", "PS2", "PS3", "PS4", "PSP"].includes(game.Platform)
			);
		case "xbox":
			return games.filter((game) =>
				["X360", "XB", "XOne"].includes(game.Platform)
			);
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
	if (games.length === 0)
		wrapper.innerHTML = `<p>No games found for search query/filter options.</p>`;
	else if (currentLayout === "table") {
		wrapper.innerHTML = renderGamesDataTable(games);
		setupSortingButtons();
	} else if (currentLayout === "grid")
		wrapper.innerHTML = renderGamesDagamerid(games);
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

	const titleButton = document.getElementById("sort-title");
	titleButton.addEventListener("click", makeSortHandler("GameTitle"));

	const categoryButton = document.getElementById("sort-category");
	categoryButton.addEventListener("click", makeSortHandler("Category"));

	const platformButton = document.getElementById("sort-platform");
	platformButton.addEventListener("click", makeSortHandler("Platform"));

	const publisherButton = document.getElementById("sort-publisher");
	publisherButton.addEventListener("click", makeSortHandler("Publisher"));

	const salesGlobalButton = document.getElementById("sort-sales-global");
	salesGlobalButton.addEventListener("click", makeSortHandler("Global"));
}

function renderGamesDataTable(games) {
	return `<table>
    <caption>HTML Games and CSS properties</caption>
    <thead>
		<tr>
			<th>
				<button type="button" id="sort-title">Game</button>
			</th>
			<th>
				<button type="button" id="sort-category">Category</button>
			</th>
			<th>
				<button type="button" id="sort-platform">Platform</button>
			</th>
			<th>
				<button type="button" id="sort-publisher">Publisher</button>
			</th>
			<th>
				<button type="button" id="sort-sales-global">Global sales</button>
			</th>
		</tr>
    </thead>
    <tbody>
        ${games
			.map(
				(game) => `<tr>
	<td>
		<p>${game.GameTitle}</p>
	</td>
	<td>
		<p>${game.Category}</p>
	</td>
	<td>
		<p>${game.Platform}</p>
	</td>
	<td>
		<p>${game.Publisher}</p>
	</td>
	<td>
		<p>${game.Global}mm</p>
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
                        <strong class="card-heading">${game.GameTitle}</strong>
                        <span class="card-subheading">${game.Platform}</span>
                    </div>
                    <p class="card-body">${game.Category} - published by ${game.Publisher} - ${game.Global}mm global profit</p>
                </div>`
		)
		.join("\n")}
    </grid>`;
}
