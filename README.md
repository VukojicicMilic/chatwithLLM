# chatwithLLM

## Why?

+ Each interaction with online LLM models costs!
"That's nearly 1.7 billion gallons—enough to fill over 2,500 Olympic-sized swimming pools. According to researchers like Shaolei Ren at the University of California, Riverside, the water consumption required to handle just 5-50 prompts on ChatGPT is around 500 milliliters per interaction."
source: https://www.linkedin.com/pulse/how-much-water-does-chatgpt-really-consume-russell-anderson-williams-irl6e/

+ Privacy and Data collection
source: https://www.gnu.org/philosophy/who-does-that-server-really-serve.html
  

## chat with Ollama models GUI
+ you can chat with chosen model
+ you can import txt and pdf files into the model
+ you can export chat into txt or pdf 

## To use the programs you will need: 
+ pyhton3 
+ pip install pytesseract
+ pandoc (for example for Ubuntu/Debian based distros sudo apt-get install pandoc)
+ ollama 

## If you want to use just one model you can use ollama-chat.py, but you can change the model in the code:
+ ["ollama", "run", "granite3.1-dense:2b"]
+ "granite3.1-dense:2b" -> use model of your choice
  
## If you want to choose from all ollama models you will use ollama-chat-all-models.py

