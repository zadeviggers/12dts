const wrapper = document.getElementById("tags-data-wrapper");
const changeLayoutDropdown = document.getElementById("change-layout-dropdown");
const changeTagFilterDropdown = document.getElementById(
	"change-tag-filter-dropdown"
);
let currentLayout = "grid";
let currentFilterMode = "all";
let filteredSortedTags = tagsData;

changeTagFilterDropdown.addEventListener("change", (event) => {
	currentFilterMode = event.target.value;
	filteredSortedTags = filterTags(tagsData, currentFilterMode);
	renderTagsData(filteredSortedTags, currentLayout);
});

changeLayoutDropdown.addEventListener("change", (event) => {
	currentLayout = event.target.value;
	renderTagsData(filteredSortedTags);
});

function filterTags(tags, filterMode) {
	switch (filterMode) {
		case "html":
			return tags.filter((tag) => tag.type === "html");
		case "css":
			return tags.filter((tag) => tag.type === "css");
		case "all":
			return tags;
		default:
			return tags;
	}
}

function renderTagsData(tags) {
	if (currentLayout === "table") {
		console.info("Rendering table layout");
		wrapper.innerHTML = renderTagsDataTable(tags);
	} else if (currentLayout === "grid") {
		console.info("Rendering grid layout");
		wrapper.innerHTML = renderTagsDataGrid(tags);
	}
}

function renderTagsDataTable(tags) {
	return `<table>
    <caption>HTML Tags and CSS properties</caption>
    <thead>
        <tr>
            <th>Language</th>
            <th>Tag</th>
            <th>Description</th>
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
