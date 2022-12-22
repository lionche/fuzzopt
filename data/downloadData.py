from datasets import load_dataset

ds = load_dataset("codeparrot/github-code", split="train", languages=["JavaScript"], streaming=False)
ds.save_to_disk('/root/fuzzopt/data/github_js')
# print(next(iter(ds)))
