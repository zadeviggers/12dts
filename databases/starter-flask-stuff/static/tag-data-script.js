const wrapper = document.getElementById("tags-data-wrapper");
const changeLayoutDropdown = document.getElementById("change-layout-dropdown");
let currentLayout = "table";

changeLayoutDropdown.addEventListener("change", (event) => {
	const layout = event.target.value;
	if (layout === "table" && currentLayout !== "table") {
		console.info("Rendering table layout");
		currentLayout = "table";
		wrapper.innerHTML = renderTagsDataTable(tagsData);
	} else if (layout === "grid" && currentLayout !== "grid") {
		console.info("Rendering grid layout");
		currentLayout = "grid";
		wrapper.innerHTML = renderTagsDataGrid(tagsData);
	}
});

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
