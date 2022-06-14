const wrapper = document.getElementById("tags-data-wrapper");
const changeLayoutDropdown = document.getElementById("change-layout-dropdown");
const changeTagFilterDropdown = document.getElementById(
	"change-tag-filter-dropdown"
);
let currentLayout = "table";
let currentFilterMode = "all";
let filteredSortedTags = tagsData;
let sortDirection = "down";
let sortColumn = "type";

// "Hydrate" the UI
changeTagFilterDropdown.addEventListener("change", (event) => {
	currentFilterMode = event.target.value;
	filteredSortedTags = applySortingAndFiltering();
	renderTagsData(filteredSortedTags);
});

changeLayoutDropdown.addEventListener("change", (event) => {
	currentLayout = event.target.value;
	filteredSortedTags = applySortingAndFiltering();
	renderTagsData(filteredSortedTags);
});

setupSortingButtons();

function applySortingAndFiltering() {
	let filtered = filterTags(tagsData);
	if (currentLayout !== "table") return filtered;
	let sorted = sortTags(filtered);
	return sorted;
}

function filterTags(tags) {
	switch (currentFilterMode) {
		case "html":
			return tags.filter((tag) => tag.type === "HTML");
		case "css":
			return tags.filter((tag) => tag.type === "CSS");
		case "all":
			return tags;
		default:
			return tags;
	}
}

function sortTags(tags) {
	return tags.sort((a, b) => {
		if (a[sortColumn] === b[sortColumn]) return 0;
		if (sortDirection === "down") {
			return a[sortColumn] < b[sortColumn] ? -1 : 1;
		} else {
			return a[sortColumn] > b[sortColumn] ? -1 : 1;
		}
	});
}

function renderTagsData(tags) {
	if (currentLayout === "table") {
		console.info("Rendering table layout");
		wrapper.innerHTML = renderTagsDataTable(tags);
		setupSortingButtons();
	} else if (currentLayout === "grid") {
		console.info("Rendering grid layout");
		wrapper.innerHTML = renderTagsDataGrid(tags);
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
		filteredSortedTags = applySortingAndFiltering();
		renderTagsData(filteredSortedTags);
	};
}

function setupSortingButtons() {
	if (currentLayout !== "table") return null;

	const typeButton = document.getElementById("sort-type");
	const tagButton = document.getElementById("sort-tag");
	const descriptionButton = document.getElementById("sort-description");
	typeButton.addEventListener("click", makeSortHandler("type"));
	tagButton.addEventListener("click", makeSortHandler("raw_tag")); // Raw tag is the tag name without the <>
	descriptionButton.addEventListener("click", makeSortHandler("description"));
}

function renderTagsDataTable(tags) {
	return `<table>
    <caption>HTML Tags and CSS properties</caption>
    <thead>
		<tr>
			<th>
				<button type="button" id="sort-type">Type</button>
			</th>
			<th>
				<button type="button" id="sort-tag">Tag</button>
			</th>
			<th>
				<button type="button" id="sort-description">Description</button>
			</th>
		</tr>
    </thead>
    <tbody>
        ${tags
			.map(
				(tag) => `<tr>
                <td>
                    <p>${tag.type}</p>
                </td>
                <td>
                    <code>
                        ${tag.tag}
                    </code>
                </td>
                <td>
                    <p>${tag.description}</p>
                </td>
            </tr>`
			)
			.join("\n")}
    </tbody>
</table>`;
}

function renderTagsDataGrid(tags) {
	return `<div class="card-grid">
    ${tags
		.map(
			(tag) =>
				`<div class="card">
                    <div class="card-header">
                        <strong class="card-heading">${tag.tag}</strong>
                        <span class="card-subheading">${tag.type}</span>
                    </div>
                    <p class="card-body">${tag.description}</p>
                </div>`
		)
		.join("\n")}
    </grid>`;
}
