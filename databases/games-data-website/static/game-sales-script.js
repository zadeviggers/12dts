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
			return games.filter((game) => game.platform === "PC");
		case "atari":
			return games.filter((game) => game.platform === "2600");
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
				].includes(game.platform)
			);

		case "ps":
			return games.filter((game) =>
				["PS", "PS2", "PS3", "PS4", "PSP"].includes(game.platform)
			);
		case "xbox":
			return games.filter((game) =>
				["X360", "XB", "XOne"].includes(game.platform)
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
	return (event) => {
		if (column === sortColumn) {
			sortDirection = sortDirection === "down" ? "up" : "down";
		} else {
			sortDirection = "down";
		}
		sortColumn = column;
		console.log("Sorting by", column, sortDirection);
		filteredSortedGames = applySortingAndFiltering();
		renderGamesData(filteredSortedGames);
		const newSortButton = document.getElementById(event.target.id);
		newSortButton.focus();
		document
			.querySelectorAll(".table-sort-button")
			.forEach((element) =>
				element.removeAttribute("data-sort-direction")
			);
		newSortButton.setAttribute("data-sort-direction", sortDirection);
	};
}

function setupSortingButtons() {
	if (currentLayout !== "table") return null;

	const titleButton = document.getElementById("sort-title");
	titleButton.addEventListener("click", makeSortHandler("title"));

	const categoryButton = document.getElementById("sort-genre");
	categoryButton.addEventListener("click", makeSortHandler("genre"));

	const platformButton = document.getElementById("sort-platform");
	platformButton.addEventListener("click", makeSortHandler("platform"));

	const publisherButton = document.getElementById("sort-publisher");
	publisherButton.addEventListener("click", makeSortHandler("publisher"));

	const salesGlobalButton = document.getElementById("sort-sales-global");
	salesGlobalButton.addEventListener("click", makeSortHandler("sales"));

	const salesYearButton = document.getElementById("sort-year");
	salesYearButton.addEventListener("click", makeSortHandler("year"));
}

function renderGamesDataTable(games) {
	return `<table>
    <thead>
		<tr>
			<th>
				<button type="button" id="sort-title" class="table-sort-button">Game</button>
			</th>
			<th>
				<button type="button" id="sort-genre" class="table-sort-button">Genre</button>
			</th>
			<th>
				<button type="button" id="sort-platform" class="table-sort-button">Platform</button>
			</th>
			<th>
				<button type="button" id="sort-publisher" class="table-sort-button">Publisher</button>
			</th>
			<th>
				<button type="button" id="sort-sales-global" title="globaly, in millions" class="table-sort-button">Sales</button>
			</th>
			<th>
				<button type="button" id="sort-year" class="table-sort-button">Year</button>
			</th>
		</tr>
    </thead>
    <tbody>
        ${games
			.map(
				(game) => `<tr>
	<td>
		<p>${game.title}</p>
	</td>
	<td>
		<p>${game.genre}</p>
	</td>
	<td>
		<p>${game.platform}</p>
	</td>
	<td>
		<p>${game.publisher}</p>
	</td>
	<td>
		<p>${game.sales}</p>
	</td>
	<td>
		<p>${game.year}</p>
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
                        <strong class="card-heading">${game.title}</strong>
                        <span class="card-subheading">${game.platform}</span>
                    </div>
                    <p class="card-body">${game.genre} - published by ${game.publisher} - ${game.sales} million global sales</p>
                </div>`
		)
		.join("\n")}
    </grid>`;
}

// Magical doublescrolling from here: https://stackoverflow.com/a/56952952
function doubleScroll(element) {
	var scrollbar = document.createElement("div");
	scrollbar.appendChild(document.createElement("div"));
	scrollbar.style.overflow = "auto";
	scrollbar.style.overflowY = "hidden";
	scrollbar.firstChild.style.width = element.scrollWidth + "px";
	scrollbar.firstChild.style.paddingTop = "1px";
	scrollbar.firstChild.appendChild(document.createTextNode("\xA0"));
	var running = false;
	scrollbar.onscroll = function () {
		if (running) {
			running = false;
			return;
		}
		running = true;
		element.scrollLeft = scrollbar.scrollLeft;
	};
	element.onscroll = function () {
		if (running) {
			running = false;
			return;
		}
		running = true;
		scrollbar.scrollLeft = element.scrollLeft;
	};
	element.parentNode.insertBefore(scrollbar, element);
}

document
	.querySelectorAll("[data-double-scroll]")
	.forEach((element) => doubleScroll(element));
