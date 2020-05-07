async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    return null;
  }
  return response.json();
}

// DataIndices
let dataIndicesToTagInfo = null;

async function updateDataIndicesInfo(model, dataset){
    const params = new URLSearchParams({model, dataset})
    dataIndicesToTagInfo = (await fetchJSON(`./data_indices?${params}`)) || {};
}

export async function getDataIndices(model, dataset){
    await updateDataIndicesInfo(model, dataset);
    return Object.keys(dataIndicesToTagInfo);
}

// Data
let dataInfo = null;

async function updateDataInfo(model, dataset, index){
    const params = new URLSearchParams({model, dataset, index})
    dataInfo = (await fetchJSON(`./data?${params}`)) || {};
}

export async function getDataInfo(model, dataset, index){
    await updateDataInfo(model, dataset, index);
    return dataInfo;
}
