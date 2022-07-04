const wrapper = document.getElementById("players-data-wrapper");
const changeLayoutDropdown = document.getElementById("change-layout-dropdown");
const changePlayerFilterDropdown = document.getElementById(
	"change-country-filter-dropdown"
);
const searchParams = new URLSearchParams(location.search);
const searchText = searchParams.get("search-text");
let currentLayout = searchParams.get("layout") || "table";
let currentFilterMode = searchParams.get("country") || "all";
let sortDirection = "down";
let sortColumn = "high_score";
let filteredSortedPlayers = applySortingAndFiltering(playersData);

// First render
renderPlayersData(filteredSortedPlayers);

// "Hydrate" the UI
changePlayerFilterDropdown.value = currentFilterMode;
changePlayerFilterDropdown.addEventListener("change", (event) => {
	currentFilterMode = event.target.value;
	searchParams.set("country", currentFilterMode);
	updateURLWithSearchParams();
	filteredSortedPlayers = applySortingAndFiltering();
	renderPlayersData(filteredSortedPlayers);
});

changeLayoutDropdown.value = currentLayout;
changeLayoutDropdown.addEventListener("change", (event) => {
	currentLayout = event.target.value;
	searchParams.set("layout", currentLayout);
	updateURLWithSearchParams();
	filteredSortedPlayers = applySortingAndFiltering();
	renderPlayersData(filteredSortedPlayers);
});

function updateURLWithSearchParams() {
	history.pushState(
		{},
		null,
		`/cricket-stats${"?" + searchParams.toString()}`
	);
}

function applySortingAndFiltering() {
	let filtered = filterPlayers(playersData);
	if (currentLayout !== "table") return filtered;
	let sorted = sortPlayers(filtered);
	return sorted;
}

function filterPlayers(players) {
	console.info(`Filtering to platofrm: ${currentFilterMode}`);
	if (currentFilterMode === "all") return players;
	return players.filter((player) => player.country === currentFilterMode);
}

function sortPlayers(players) {
	if (sortDirection === "none") return players;
	return players.sort((a, b) => {
		if (a[sortColumn] === b[sortColumn]) return 0;
		if (sortDirection === "down") {
			return a[sortColumn] > b[sortColumn] ? -1 : 1;
		} else {
			return a[sortColumn] < b[sortColumn] ? -1 : 1;
		}
	});
}

function renderPlayersData(players) {
	if (players.length === 0)
		wrapper.innerHTML = `<p>No players found for search query/filter options.</p>`;
	else if (currentLayout === "table") {
		wrapper.innerHTML = renderPlayersDataTable(players);
		setupSortingButtons();
	} else if (currentLayout === "grid")
		wrapper.innerHTML = renderPlayersDataGrid(players);
}

function makeSortHandler(column) {
	return (event) => {
		if (column === sortColumn) {
			if (sortDirection === "down") sortDirection = "up";
			else if (sortDirection === "up") sortDirection = "none";
			else sortDirection = "down";
		} else {
			sortDirection = "down";
		}
		sortColumn = column;
		console.log("Sorting by", column, sortDirection);
		filteredSortedPlayers = applySortingAndFiltering();
		renderPlayersData(filteredSortedPlayers);
		const newSortButton = document.querySelector(
			`[data-sort-column="${column}"]`
		);
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

	const sortButtons = document.querySelectorAll(".table-sort-button");
	sortButtons.forEach((button) => {
		const column = button.getAttribute("data-sort-column");
		button.addEventListener("click", makeSortHandler(column));
	});
}

function renderPlayersDataTable(players) {
	return `<table>
    <thead>
		<tr>
			<th>
				<button type="button" data-sort-column="name" class="table-sort-button">Player</button>
			</th>
			<th>
				<button type="button" data-sort-column="country" class="table-sort-button">Country</button>
			</th>
			<th>
				<button type="button" data-sort-column="matches" class="table-sort-button">Matches</button>
			</th>
			<th>
				<button type="button" data-sort-column="innings" class="table-sort-button">Innings</button>
			</th>
			<th>
				<button type="button" data-sort-column="not_outs" class="table-sort-button">Not Outs</button>
			</th>
			<th>
				<button type="button" data-sort-column="runs" class="table-sort-button">Runs</button>
			</th>
			<th>
				<button type="button" data-sort-column="high_score" class="table-sort-button">High Score</button>
			</th>
			<th>
				<button type="button" data-sort-column="average" class="table-sort-button">Average</button>
			</th>
			<th>
				<button type="button"
						data-sort-column="balls_faced"
						class="table-sort-button">Balls Faced</button>
			</th>
			<th>
				<button type="button"
						data-sort-column="strike_rate"
						class="table-sort-button">Strike Rate</button>
			</th>
		</tr>
    </thead>
    <tbody>
        ${players
			.map(
				(player) => `<tr>
	<td>
		<p>${player.name}</p>
	</td>
	<td>
		<p>${player.country}</p>
	</td>
	<td>
		<p>${player.matches}</p>
	</td>
	<td>
		<p>${player.innings}</p>
	</td>
	<td>
		<p>${player.not_outs}</p>
	</td>
	<td>
		<p>${player.runs}</p>
	</td>
	<td>
		<p>${player.high_score}</p>
	</td>
	<td>
		<p>${player.average}</p>
	</td>
	<td>
		<p>${player.balls_faced}</p>
	</td>
	<td>
		<p>${player.strike_rate}</p>
	</td>
</tr>`
			)
			.join("\n")}
    </tbody>
</table>`;
}

function renderPlayersDataGrid(players) {
	return `<div class="card-grid">
    ${players
		.map(
			(player) =>
				`<div class="card">
                    <div class="card-header">
                        <strong class="card-heading">${player.name}</strong>
                        <span class="card-subheading">${player.country}</span>
                    </div>
                    <p class="card-body">${player.matches} matches • ${player.innings} innings •  ${player.runs} runs • ${player.average} average • ${player.strike_rate} strike rate.</p>
                </div>`
		)
		.join("\n")}
    </grid>`;
}

// Magical doublescrolling from here: https://stackoverflow.com/a/56952952
// I added the resize observer and upgraded this to some more modern javscript then I updated the original answer
function doubleScroll(element) {
	const scrollbar = document.createElement("div");
	scrollbar.appendChild(document.createElement("div"));
	scrollbar.style.overflow = "auto";
	scrollbar.style.overflowY = "hidden";
	scrollbar.firstChild.style.width = element.scrollWidth + "px";
	scrollbar.firstChild.style.paddingTop = "1px";
	scrollbar.firstChild.appendChild(document.createTextNode("\xA0"));
	let running = false;
	// Keep scrollbar in sync when element size changes
	new ResizeObserver(() => {
		scrollbar.firstChild.style.width = element.scrollWidth + "px";
	}).observe(element);
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
