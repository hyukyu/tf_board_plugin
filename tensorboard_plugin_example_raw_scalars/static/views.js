// Copyright 2019 The TensorFlow Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// =============================================================================

// Generic view builders.

/**
 * @param {!Map<string, !Array<Object>>} tagsToScalars
 * @return {!DocumentFragment}
 */
// export function createPreviews(tagsToScalars) {
//   const fragment = document.createDocumentFragment();
//
//   if (!tagsToScalars.size) {
//     const messageElement = createElement('h2');
//     messageElement.textContent = 'No tags found.';
//     fragment.appendChild(messageElement);
//     return fragment;
//   }
//
//   /**
//    * For each tag, build UI in this form:
//    *   <div class="preview">
//    *     <div class="tagname">${tag}</div>
//    *     <textarea class="preview-text">${result}</textarea>
//    *   </div>
//    */
//   for (let [tag, scalars] of tagsToScalars) {
//     const previewEl = createElement('div', 'preview');
//     const tagNameEl = createElement('div', 'tagname');
//     const textPreviewEl = createElement('textarea', 'preview-text');
//     tagNameEl.textContent = tag;
//     textPreviewEl.textContent = scalars
//       ? JSON.stringify(scalars)
//       : 'No scalar data found.';
//     previewEl.appendChild(tagNameEl);
//     previewEl.appendChild(textPreviewEl);
//     fragment.appendChild(previewEl);
//   }
//   return fragment;
// }


export function createPreviews(dataInfo){
  const fragment = document.createDocumentFragment();
  if (Object.keys(dataInfo).length == 0){
    alert("bad size");
    const messageElement = createElement('h2');
    messageElement.textContent = 'No data selected.';
    fragment.appendChild(messageElement);
    return fragment;
  }
  for (let [tag, value] of Object.entries(dataInfo)){
    const element = createElement('div', tag);
    const textPreviewEL = createElement('textarea', tag.concat('-text'))
    textPreviewEL.textContent = value;
    element.appendChild(textPreviewEL);
    fragment.appendChild(element);
  }
  return fragment;
}


/**
 * @param {string} tag
 * @param {string=} className
 * @return {!Element}
 */
function createElement(tag, className) {
  const result = document.createElement(tag);
  if (className) {
    result.className = className;
  }
  return result;
}


// Appended codes from now on

export function createModelSelector(models){
    /**
   * Build a component in this form:
   *   <select class="model-selector">
   *     <option value="${run}">${run}</option>
   *     ...
   *   </select>
   */
  const element = createElement('select', 'model-selector');
  for (const model of models){
    element.options.add(new Option(model, model));
  }
  return element;
}

export function createDatasetSelector(datasets){
  const element = createElement('select', 'dataset-selector');
  for (const dataset of datasets){
    element.options.add(new Option(dataset, dataset));
  }
  return element;
}

export function createDataSelector(data){
  const element = createElement('select', 'data-selector');
  for (const item of data){
    element.options.add(new Option(item, item));
  }
  return element;
}
