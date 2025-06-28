from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class DroneLLM:
    def __init__(self, model_path="meta-llama/Llama-2-7b-chat-hf", max_history=3):
        print("Loading model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
        self.model.eval()
        self.history = []
        self.max_history = max_history
        print("Model loaded successfully.")

    def build_prompt(self, context_messages, new_input):
        messages = [
            {"role": "system", "content": "You are a helpful assistant for autonomous drone decision-making."}
        ]
        for message in context_messages:
            messages.append({"role": "user", "content": message})
        messages.append({"role": "user", "content": new_input})

        try:
            return self.tokenizer.apply_chat_template(messages, tokenize=False)
        except Exception as e:
            print(f"[WARN] Fallback to plain format due to: {e}")
            full_prompt = "System: You are a helpful assistant for drones.\n"
            for msg in context_messages:
                full_prompt += f"Drone: {msg}\n"
            full_prompt += f"Drone: {new_input}\nLLM:"
            return full_prompt

    def process_message(self, new_input):
        self.history.append(new_input)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        prompt = self.build_prompt(self.history[:-1], self.history[-1])
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_length=200,
                temperature=0.7,
                top_p=0.95,
                do_sample=True
            )

        full_output = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return self._extract_response(full_output, prompt)

    def _extract_response(self, full_text, prompt):
        return full_text[len(prompt):].strip()
