pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.6.347/pdf.worker.min.js";

async function extractTextFromFile(file) {
    return new Promise((resolve) => {
        if (file.type === "application/pdf") {
            const reader = new FileReader();
            reader.onload = async (event) => {
                const pdfData = new Uint8Array(event.target.result);
                const pdfDoc = await pdfjsLib.getDocument({ data: pdfData }).promise;
                const numPages = pdfDoc.numPages;
                let text = "";

                for (let i = 1; i <= numPages; i++) {
                    const page = await pdfDoc.getPage(i);
                    const content = await page.getTextContent();
                    text += content.items.map((item) => item.str).join(" ");
                }
                resolve(text);
            };
            reader.readAsArrayBuffer(file);
        } else if (file.type === "text/plain") {
            const reader = new FileReader();
            reader.onload = (event) => {
                resolve(event.target.result);
            };
            reader.readAsText(file);
        } else {
            resolve(null);
        }
    });
}

document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("doc-file");
    const file = fileInput.files[0];
    const content = document.getElementById("doc-content").value;

    if (!file && !content) {
        alert("Nothing to upload!!!");
        return;
    }

    document.getElementById("loading").classList.remove("d-none");

    let text;
    if (file) {
        text = await extractTextFromFile(file);
    } else {
        text = content;
    }

    try {
        const formData = new FormData();
        formData.append("content", text);

        const response = await fetch("http://127.0.0.1:8000/api/upload", {
            method: "POST",
            body: formData,
        });

        if (response.status === 200) {
            const data = await response.json();
            if (data.status === "success") {
                alert("Upload successful!!!");
            } else {
                console.log('success')
                alert("Sorry!! Error during upload.");
            }
        } else {
            alert("Sorry!! Error during upload.");
        }
    } catch (error) {
        console.error(error);
        alert("Sorry!! Error during upload.");
    } finally {
        document.getElementById("loading").classList.add("d-none");
    }
});


async function search(query) {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/search?query=${encodeURIComponent(query)}`);
  
      if (!response.ok) {
        throw new Error("Sorry!! Error during the Search.");
      }
  
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Sorry!! Error during the Search.", error);
    }
  }
  
  function displaySearchResults(results) {
    const resultsDiv = document.getElementById("search-results");
    resultsDiv.innerHTML = "";
  
    if (!results || results.length == 0) {
      resultsDiv.innerHTML = "<p>Nothing found to list.</p>";
      return;
    }
  
    const list = document.createElement("ul");
    list.classList.add("list-group");
  
    results.forEach(result => {
      const listItem = document.createElement("li");
      listItem.classList.add("list-group-item");
  
      const text = result[0];
      const entities = result[1];
      listItem.innerHTML = `<em>Text found related:</em> ${text}<br>`;
      
      if (entities.length > 0) {
        listItem.innerHTML += `<em>Entity being referred to:</em><br>`;
        entities.forEach(entity => {
          listItem.innerHTML += `${entity[0]} (${entity[1]})<br>`;
        });
      } else {
        listItem.innerHTML += "<em>No entities related to text found</em>";
      }
  
      list.appendChild(listItem);
    });
  
    resultsDiv.appendChild(list);
}
  

document.getElementById("search-form").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const query = document.getElementById("search-query").value;
  
    if (!query) {
      alert("Please enter a query to search.");
      return;
    }
  
    const results = await search(query);
    displaySearchResults(results);
  });
  
