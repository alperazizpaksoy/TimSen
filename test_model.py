import google.generativeai as genai

# Buraya güncel API anahtarını yapıştır
genai.configure(api_key="AIzaSyDU2TSv2ClKJqVCza0jMahwBNEEywyvuVs")

print("Kullanabileceğin Modeller:")
print("-" * 30)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)