# References

- NLLB Team (2024). Scaling neural machine translation to 200 languages. *Nature* 630, 841–846. https://doi.org/10.1038/s41586-024-07335-x
- NLLB Team (2022). No Language Left Behind: scaling human-centered machine translation. arXiv:2207.04672. https://arxiv.org/abs/2207.04672
- Goyal, N. et al. (2022). The FLORES-101 evaluation benchmark for low-resource and multilingual machine translation. *TACL* 10, 522–538. https://aclanthology.org/2022.tacl-1.30
- Artetxe, M. and Schwenk, H. (2019). Margin-based parallel corpus mining with multilingual sentence embeddings. *ACL 2019*. https://aclanthology.org/P19-1309
- Feng, F. et al. (2022). Language-agnostic BERT sentence embedding. *ACL 2022*, 878–891. https://aclanthology.org/2022.acl-long.62
- Wang, L. et al. (2024). Multilingual E5 text embeddings: a technical report. arXiv:2402.05672. https://arxiv.org/abs/2402.05672
- Senel, L. K., Ebing, B., Baghirova, K., Schütze, H. and Glavaš, G. (2024). Kardeş-NLU: transfer to low-resource languages with the help of a high-resource cousin – a benchmark and evaluation for Turkic languages. *EACL 2024*, 1672–1688. https://aclanthology.org/2024.eacl-long.100
- Geifman, Y. and El-Yaniv, R. (2017). Selective classification for deep neural networks. *NeurIPS 2017*. https://arxiv.org/abs/1705.08500

## How this project relates
Cross-lingual sentence retrieval on FLORES-style data is an established test (bitext mining). What v0.1 adds is narrow: the five Turkic languages across two scripts, a transliteration baseline, and an open-set test where the retriever must abstain when the true sentence is missing. It does not claim a new retrieval method.
