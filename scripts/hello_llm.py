from studypilot.llm import get_llm

llm = get_llm()
response = llm.invoke("Erkläre in einem Satz, was ein KI-Agent ist.")
print(response.content)