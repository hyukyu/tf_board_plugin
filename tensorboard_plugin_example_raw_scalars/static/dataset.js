let datasetToTagInfo = null;

async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    return null;
  }
  return response.json();
}

async function updateDatasetInfo(model){
    const params = new URLSearchParams({model})
    datasetToTagInfo = (await fetchJSON(`./datasets?${params}`)) || {};
}

export async function getDatasets(model){
    await updateDatasetInfo(model);
    return Object.keys(datasetToTagInfo);
}
