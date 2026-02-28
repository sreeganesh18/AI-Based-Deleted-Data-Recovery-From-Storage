Technical Specification and Product Requirements for AI-Powered Autonomous File Carving and Reconstruction Systems
Executive Summary
The escalating volume of digital evidence and the growing sophistication of anti-forensic techniques necessitate a transition from traditional metadata-reliant data recovery to intelligent, content-based reconstruction systems. This report details the requirements for a high-performance, AI-driven platform designed to recover a wide array of deleted file types from raw disk images. The architecture bypasses the inherent vulnerabilities of corrupted file system metadata by employing advanced deep learning models—specifically 1D-Convolutional Neural Networks (1D-CNNs) and Swin Transformers—to identify and classify file fragments at the block level.1 By integrating graph-based reassembly algorithms and generative AI for data imputation, the system addresses the critical challenge of non-contiguous fragmentation and partial data loss.3 Optimized for local deployment on the AMD Ryzen 9 architecture, the system leverages hardware-specific acceleration through PyTorch and Intel Extension for PyTorch (IPEX) to achieve forensic-grade accuracy with commercial-grade speed.5
Forensic Context and the Failure of Traditional Metadata Recovery
Digital forensic investigations increasingly encounter scenarios where file system metadata, such as the Master File Table (MFT) in NTFS or the inode tables in EXT4, are intentionally obliterated or naturally corrupted.1 Traditional recovery tools typically rely on these metadata structures to locate and reassemble files. When these pointers are missing, the only recourse is file carving—the process of extracting files based solely on their internal content and structure.1 However, the landscape of data storage has evolved, introducing complexities that render basic signature-based carving (searching for headers and footers) insufficient.9
The prevalence of file fragmentation—where a single file is stored in non-contiguous clusters across a disk—presents a significant hurdle.11 As disk occupancy increases, operating systems are forced to scatter file data, making simple linear carving impossible. Furthermore, modern storage technologies such as Solid-State Drives (SSDs) utilize background processes like TRIM, which proactively clear unallocated blocks, thereby reducing the window of opportunity for recovery.10 Anti-forensic measures, including intermittent encryption and deep wiping, further complicate the process by altering the statistical signatures of file fragments.13 The requirements outlined in this document are intended to address these challenges through an automated, intelligent pipeline capable of performing "blind" recovery across diverse file formats.14
Technical Logic for High-Performance Scanning
The initial phase of recovery involves the ingestion of raw binary data from disk images, which often range from gigabytes to multiple terabytes. The system requires a low-level scanning module that operates with block-level granularity, typically 512 bytes or 4096 bytes, to mirror the logical sector sizes of modern storage devices.11
Entropy-Based Profiling and Triage
To manage the computational load of deep learning classification, the scanner must implement an initial triage layer using statistical features. High-entropy profiling is used to distinguish between compressed, encrypted, and plaintext data.9 This distinction is vital; for instance, a block with entropy approaching 8.0 bits per byte is likely encrypted or highly compressed, requiring different handling than a low-entropy text fragment. The scanner utilizes Shannon entropy and N-gram distribution analysis to create a preliminary profile of each block before passing it to the neural network.1
Scanner Feature
Description
Forensic Utility
Block-Level I/O
Reads raw sectors directly from the image file via mmap.
Minimizes memory overhead and maximizes sequential throughput.
Entropy Mapping
Calculates the byte-level entropy for every 512B/4096B block.
Identifies potentially encrypted or compressed regions.
Offset Logging
Records the exact physical sector address for every fragment.
Essential for reassembly and maintaining the chain of custody.
Signature Detection
Identifies known "magic numbers" for contiguous files.
Provides high-confidence anchors for the reassembly engine.

The efficiency of this module is enhanced by the AMD Ryzen 9's high core count and large cache, which allows for parallel processing of multiple disk regions simultaneously. By utilizing asynchronous I/O operations in Python, the scanner can saturate the memory bus, ensuring that the AI classification layers are never idle.6
AI-Powered Fragment Classification
At the core of the system is a multi-modal classification architecture designed to identify the file type of isolated data blocks. This module must handle fragments that lack header or footer information, a task traditionally considered nearly impossible in forensics.1
Depthwise Separable Convolutional Neural Networks (DSC-CNN)
For rapid, real-time classification, the system employs a 1D-CNN architecture optimized with depthwise separable convolutions.1 Standard convolutional layers are computationally expensive because they process all channels and spatial dimensions simultaneously. Depthwise separable convolutions split this into two stages: a depthwise convolution that applies a single filter to each input channel and a pointwise convolution that combines the outputs.11
This factorized approach results in a 4x reduction in model size and a 6x improvement in inference speed while maintaining high accuracy.1 To further improve performance, Squeeze-and-Excitation (SE) blocks are integrated. These blocks use a global average pooling layer to squeeze spatial information into a channel descriptor, followed by two fully connected layers that recalibrate the channel weights.1 This allows the model to "attend" to the most relevant features of a binary fragment, such as specific byte frequencies or patterns characteristic of particular file formats.1
Swin Transformer V2 and Sequential Dependencies
While CNNs excel at local feature extraction, the system also requires a mechanism to capture long-range dependencies across bytes. The CarveFormer module, based on the Swin Transformer V2, is implemented for this purpose.2 Unlike standard Transformers that suffer from quadratic complexity relative to sequence length, the Swin Transformer uses shifted windows to limit self-attention to local neighborhoods while still allowing for hierarchical pattern recognition through layer merging.2
The input bytes are first passed through a trainable embedding layer that converts each 8-bit byte into a continuous vector space of 32 or 96 dimensions.2 This transformation allows the model to treat binary data with the same mathematical rigor as natural language or image pixels. The self-attention mechanism then evaluates the relationship between every byte in the window, identifying complex, non-linear structures that characterize formats such as encrypted headers or high-redundancy media streams.16
Model Component
Parameter Count
Primary Benefit
Target File Types
DSC-SE (CNN)
~100,000
Speed and efficiency on CPU.
High-volume bitmaps and text.
Swin Transformer
~28,000,000
Deep hierarchical pattern recognition.
Compressed archives and executables.
Embedding Layer
Varies
Translates discrete bytes to continuous space.
All supported formats.
Global Avg Pooling
0
Dimensionality reduction for final classification.
N/A

The integration of these two architectures—CNN for local texture and Transformer for global structure—enables the system to support at least 75 file types with a high degree of confidence, even when fragments are as small as 512 bytes.14
Fragment Grouping and Reassembly Logic
Once fragments are classified, the system must determine the correct sequence to reconstruct the original files. This is modeled as a combinatorial optimization problem where the goal is to find the most probable chain of fragments that minimizes discontinuity.4
Graph-Based Optimization Framework
The reassembly engine treats the identified fragments as nodes in a directed graph.4 Edges between nodes represent the probability that one fragment follows another. This probability, or "affinity score," is calculated using a combination of techniques:
Byte-Level Adjacency: For uncompressed formats, the system checks for continuity in data patterns (e.g., the transition of pixel values at the edge of an image fragment).4
Semantic Prediction (LSTM): Long Short-Term Memory networks are used to predict the expected first few bytes of a successor fragment given the last bytes of the current fragment.21
Coherence of Euclidean Distance (CoEDm): This metric is particularly useful for fragmented JPEG images, as it evaluates the mathematical coherence between intertwined blocks in the scan area.26
The system uses a k-vertex disjoint path algorithm to find the optimal ordering of fragments.4 In cases of ambiguity, where multiple fragments could potentially follow a given node, a genetic algorithm is employed. The genetic algorithm maintains a population of potential reassembly solutions and uses a cost function to evolve them toward the most "natural" configuration based on the file format's syntax.26
Handling Intertwined and Non-Linear Fragmentation
In real-world scenarios, fragments from multiple files may be intertwined, a common result of modern multi-threaded operating system operations.26 The reassembly engine must be able to "de-interlace" these streams. By utilizing the classification labels from the AI module, the engine can filter out "strange blocks" or noise that do not belong to the target file's predicted format, thereby reducing the search space for the reassembly algorithms.26
Generative Data Reconstruction and Imputation
A significant challenge in data recovery is the presence of "holes" caused by overwriting or partial corruption.9 The proposed system addresses this through the integration of generative AI components capable of synthesizing missing data based on learned statistical structures.3
Diffusion Models for Binary Inpainting
Diffusion models operate through a two-stage process: a forward diffusion that adds noise to a data sample and a reverse diffusion that learns to remove that noise.29 In the context of data recovery, the corrupted or missing parts of a file are treated as "noise" or "masks." The trained model analyzes the surrounding "clean" fragments and iteratively removes the noise to reconstruct the original structure.29
This is particularly effective for repairing corrupted file headers.13 By training on millions of valid headers for 1000+ file types, the system can synthesize a functional header for a recovered data stream, allowing it to be opened by native applications.34 For more complex structural repairs, such as in PDF or ZIP files, the system employs a generative planner that proposes candidate fixes in the form of code or configuration patches.36
Performance and Fidelity Metrics for Reconstruction
The quality of reconstructed data is measured using both technical and perceptual metrics. For multimedia content, the system tracks the Peak Signal-to-Noise Ratio (PSNR) and the Structural Similarity Index (SSIM) to ensure that generative imputations do not introduce artifacts that could mislead an investigator.38 For non-media files, the system relies on format-specific syntax validation and checksum matching to ensure data integrity.15
Reconstruction Metric
Mathematical Basis
Threshold for Success
PSNR

> 30 dB for 8-bit media.
SSIM
Luminance, Contrast, and Structure comparison.
> 0.90 for visual fidelity.
Recovery Rate

> 90% in bench tests.
Temporal Accuracy

> 95% for video/audio.

Optimization for AMD Ryzen 9 and PyTorch
To be viable in the field, the system must perform these complex computations on local hardware. The AMD Ryzen 9 series, with its high core density and advanced instruction sets (AVX-512), provides an ideal environment for CPU-based deep learning acceleration.5
Hardware-Specific Acceleration Strategies
The system utilizes the Intel Extension for PyTorch (IPEX) and oneDNN to maximize the efficiency of the Zen architecture.5 Despite the Intel branding, these libraries are part of the oneAPI initiative and provide significant benefits for AMD CPUs by optimizing the execution of basic building blocks in deep learning.
Weight Prepacking: This technique involves converting model weights into a blocked memory layout during initialization.5 This layout is specifically designed to fit into the CPU's cache hierarchies, reducing the latency associated with memory fetches during inference.44
BFloat16 Training and Inference: The use of BFloat16 (16-bit brain floating-point) offers a significant performance boost on the Ryzen 9 by reducing memory bandwidth pressure and allowing more data to be processed in each clock cycle.5
Graph Fusion: The system leverages TorchScript and oneDNN graph fusion to combine multiple operations (e.g., a convolution followed by a ReLU activation) into a single optimized kernel.5
Channels-Last Optimization: For the CNN-based modules, the system uses the "channels-last" memory format (NHWC), which has been shown to improve throughput by up to 25% on modern CPU architectures.6
Local Deployment Considerations
The system's modular architecture allows it to scale across the Ryzen 9's 16+ cores. The scanning and initial entropy profiling are managed via a high-performance multi-processing pool, while the AI inference is handled through a batched execution model to maximize the utilization of the CPU's vector units.6 Memory management is critical; the system implements "in-place" carving logic where possible to avoid the overhead of writing massive intermediate files to the disk.47
Dataset and Training Strategy
The intelligence of the system is derived from its exposure to diverse and complex data scenarios during the training phase.14
Primary Training Corpora
The system's classification models are trained on the FFT-75 dataset, which encompasses 75 file formats across several categories:
Multimedia: Detailed representation of JPEG, PNG, MP4, and various RAW photograph formats (ARW, CR2, etc.).14
Archives: Support for 13 types, including 7Z, RAR, and GZ, which are historically difficult to carve due to their high entropy.14
Office Documents: Coverage for PDF, DOCX, and legacy formats.
Human-Readable Text: Training on JSON, XML, and plain text to identify subtle structural cues.14
Synthetic Data Generation for Forensic Robustness
To supplement real-world data, the system utilizes a custom dataset generation framework to simulate complex fragmentation scenarios.27 This framework allows for the automated creation of training samples that mirror the difficulties found in the field:
Intertwining: Simulating the storage of fragments from multiple files in an alternating sequence.27
Randomized Fragmentation: Splitting files into blocks of varying sizes and shuffling their order.27
Metadata Stripping: Intentionally removing headers and footers to force the model to learn content-based features.27
Noise Injection: Filling unallocated space with random data or fragments from deleted, unrelated files.27
By training on these synthetic scenarios, the AI models develop the robustness required to handle fragmented and corrupted data that standard tools would fail to recognize.16
14-Week Development Roadmap
The development of the system is organized into a 14-week academic project timeline, ensuring a structured progression from research to a production-ready MVP (Minimum Viable Product).
Phase 1: Planning and Research (Weeks 1-3)
The initial weeks are dedicated to defining the project's technical scope and establishing the development environment.50
Week 1: Finalization of the 75 target file types and collection of the GovDocs1 and FFT-75 datasets.14
Week 2: Benchmarking the local AMD Ryzen 9 system and configuring the PyTorch IPEX environment.5
Week 3: Preliminary research into graph-based reassembly algorithms and generative AI models for binary data.23
Phase 2: Data Engineering and Framework Development (Weeks 4-6)
This phase focuses on building the pipeline for data ingestion and the synthetic training environment.52
Week 4: Development of the low-level scanner (M1) and the entropy profiling module.11
Week 5: Implementation of the synthetic fragmentation framework to generate diverse training samples.27
Week 6: Data cleaning, labeling, and conversion of binary fragments into the 1D vectors required for the neural networks.11
Phase 3: Model Training and Optimization (Weeks 7-10)
The core AI modules are developed, trained, and fine-tuned during this period.51
Week 7: Training the 1D-CNN (M2) using depthwise separable convolutions and SE blocks.1
Week 8: Training the Swin Transformer V2 (CarveFormer) for high-complexity classification tasks.2
Week 9: Integration of IPEX and oneDNN optimizations, including BFloat16 mixed-precision training.5
Week 10: Initial testing of model accuracy on fragmented test sets and adjustment of hyperparameters.6
Phase 4: Reassembly and Reconstruction Integration (Weeks 11-12)
The system is integrated into a cohesive pipeline that moves from fragments to full files.51
Week 11: Implementation of the graph-based reassembly engine (M3) and the genetic algorithm for sequence refinement.4
Week 12: Deployment of the generative repair module (M4) for header restoration and data imputation.29
Phase 5: Testing, Validation, and Deployment (Weeks 13-14)
The final phase involves rigorous forensic validation and performance benchmarking.42
Week 13: Testing the full pipeline against established forensic challenges (e.g., DFRWS datasets) and measuring RR, PSNR, and SSIM.27
Week 14: Completion of the forensic validator (M6), final documentation, and preparation for deployment.15
Ethical and Legal Framework for AI-Based Recovery
The application of AI in digital forensics introduces unique ethical and legal considerations, particularly concerning the integrity of evidence and its admissibility in judicial proceedings.10
Admissibility and the Chain of Custody
For recovered data to be admissible, the recovery process must be transparent and verifiable. The system must maintain a strict chain of custody, ensuring that the original evidence is never altered.10 All recovery operations must be performed on bit-for-bit images, and the system must generate detailed logs of every action taken, including the specific model versions and weights used during classification and reconstruction.15
Handling AI Hallucinations in Evidence
A critical ethical concern is the potential for generative AI to "hallucinate" data that did not exist in the original file.32 While generative reconstruction is invaluable for restoring functionality to a corrupted document, it must be used with caution in a forensic context.
Clear Labeling: Any data generated or imputed by the AI must be clearly flagged in the final report.32
Contextual Validation: Generative repairs should be used primarily for "triage" and "contextual analysis" rather than as primary evidence unless the imputed data can be independently verified through other means.32
Transparency: The mathematical logic behind the generative models (e.g., the reverse diffusion process) must be documented to satisfy legal standards like the Daubert Standard, which requires that forensic techniques be scientifically valid and have known error rates.15
Privacy and PII Considerations
Training the system requires access to large volumes of data, which may contain personally identifiable information (PII).28 The project must adhere to strict data privacy protocols, including the use of anonymized public datasets and the deletion of any PII encountered during the generation of synthetic training sets.48 The final deployment on local, air-gapped AMD Ryzen 9 systems further mitigates privacy risks by ensuring that sensitive forensic data never leaves the investigator's control.15
Conclusion
The evolution of file carving from a manual, signature-based process to an automated, AI-driven discipline is essential for the future of digital investigations. By leveraging the advanced feature extraction capabilities of CNNs and Transformers, alongside the predictive power of generative models, the proposed system provides a robust solution for recovering data from the most challenging forensic scenarios. The local deployment on AMD Ryzen 9 systems ensures that this power is accessible to forensic practitioners without the need for expensive cloud infrastructure or specialized hardware. As the volume of digital data continues to grow, such intelligent systems will be the primary means by which investigators make sense of the residual footprints left on modern storage media. Strategic focus on continual model refinement and adherence to rigorous forensic ethics will ensure that this system remains a trusted and effective tool in the pursuit of digital truth.
Works cited
File Fragment Type Classification Using Light-Weight Convolutional, accessed on February 28, 2026, https://ieeexplore.ieee.org/iel8/6287639/10380310/10734094.pdf
(PDF) Transformer-Based File Fragment Type Classification for File, accessed on February 28, 2026, https://www.researchgate.net/publication/393049441_Transformer-Based_File_Fragment_Type_Classification_for_File_Carving_in_Digital_Forensics
ENHANCING DATA IMPUTATION WITH GENERATIVE AI, accessed on February 28, 2026, https://figshare.mq.edu.au/ndownloader/files/44478653
Automated reassembly of file fragmented images using greedy, accessed on February 28, 2026, https://www.researchgate.net/publication/3328117_Automated_reassembly_of_file_fragmented_images_using_greedy_algorithms
Accelerate PyTorch with Intel® Extension for PyTorch, accessed on February 28, 2026, https://www.intel.com/content/www/us/en/developer/articles/technical/accelerate-with-intel-extension-for-pytorch.html
Optimizing PyTorch Model Inference on CPU - Towards Data Science, accessed on February 28, 2026, https://towardsdatascience.com/optimizing-pytorch-model-inference-on-cpu/
File Carving - Digital Forensics : TryHackMe Walkthrough - Medium, accessed on February 28, 2026, https://medium.com/@RosanaFS/file-carving-digital-forensics-tryhackme-walkthrough-8d0ed2f879ec
A REVIEW OF DIGITAL FORENSICS METHODS FOR JPEG FILE, accessed on February 28, 2026, http://www.jatit.org/volumes/Vol96No17/17Vol96No17.pdf
(PDF) A Review of JPEG File Carving: Challenges, Techniques, and, accessed on February 28, 2026, https://www.researchgate.net/publication/389732142_A_Review_of_JPEG_File_Carving_Challenges_Techniques_and_Future_Directions
Recovery of Deleted Files: Challenges and Techniques - IJFMR, accessed on February 28, 2026, https://www.ijfmr.com/papers/2025/2/41088.pdf
File Fragment Classification using Light-Weight Convolutional, accessed on February 28, 2026, https://arxiv.org/pdf/2305.00656
File Carving: Analyzing Data Retrieval in Digital Forensics - ijcit, accessed on February 28, 2026, https://ijcit.com/index.php/ijcit/article/view/420/109
Innovative AI Strategies Supporting Trusted Data Recovery, accessed on February 28, 2026, https://indexengines.com/wp-content/uploads/2025/04/WP_CS_AI_Confident-Recovery.pdf
File Type Identification Classifier with Classification-by ... - SSRN, accessed on February 28, 2026, https://papers.ssrn.com/sol3/Delivery.cfm/1a987426-917a-4aa9-8563-3060cb822607-MECA.pdf?abstractid=4862624&mirid=1
Rhya – AI – Driven Digital Forensic Investigation for Automated, accessed on February 28, 2026, https://ijirt.org/publishedpaper/IJIRT177503_PAPER.pdf
Transformer-Based File Fragment Type Classification for File ..., accessed on February 28, 2026, https://papers.academic-conferences.org/index.php/eccws/article/download/3552/3277/13160
Data Recovery Techniques and Data Integrity Verification Methods, accessed on February 28, 2026, http://ijns.jalaxy.com.tw/contents/ijns-v27-n5/ijns-2025-v27-n5-p949-959.pdf
File Fragment Classification Using Grayscale Image Conversion and, accessed on February 28, 2026, https://www.computer.org/csdl/proceedings-article/spw/2018/634901a140/12UTFwBQQMw
Hierarchy-Based File Fragment Classification - MDPI, accessed on February 28, 2026, https://www.mdpi.com/2504-4990/2/3/12
(PDF) File Fragment Type Classification Using Light-Weight, accessed on February 28, 2026, https://www.researchgate.net/publication/385240361_File_Fragment_Type_Classification_using_Light-Weight_Convolutional_Neural_Networks
Exploring Sequence Models: From RNNs to Transformers - Viso Suite, accessed on February 28, 2026, https://viso.ai/deep-learning/sequential-models/
Exploring Transformer-Augmented LSTM for Temporal and Spatial, accessed on February 28, 2026, https://arxiv.org/html/2412.13419v1
A Graph-based Optimization Algorithm for Fragmented Image, accessed on February 28, 2026, https://www.researchgate.net/publication/261673917_A_Graph-based_Optimization_Algorithm_for_Fragmented_Image_Reassembly
GRAPH-BASED FORENSIC MODELING OF ... - UPC Commons, accessed on February 28, 2026, https://upcommons.upc.edu/bitstreams/e0f700cf-42d3-40cc-baa8-83391ef5bcbe/download
Explained Deep Sequence Modeling with RNN and LSTM - Medium, accessed on February 28, 2026, https://medium.com/analytics-vidhya/explained-deep-sequence-modeling-with-rnn-and-lstm-e71521f86036
A Meta-Heuristic Method for Reassemble Bifragmented Intertwined, accessed on February 28, 2026, https://ieeexplore.ieee.org/iel7/6287639/10005208/10272244.pdf
Syntactical Carving of PNGs and Automated Generation of ... - DFRWS, accessed on February 28, 2026, https://dfrws.org/wp-content/uploads/2019/06/2019_USA_paper-syntactical_carving_of_pngs_and_automated_generation_of_reproducible_datasets-1.pdf
Generative AI in Medical Practice: In-Depth Exploration of Privacy, accessed on February 28, 2026, https://pmc.ncbi.nlm.nih.gov/articles/PMC10960211/
Applications of Generative Artificial Intelligence in Brain MRI Image, accessed on February 28, 2026, https://www.scienceopen.com/hosted-document?doi=10.15212/npt-2024-0007
AI Powered Restoration of Historical Documents - AIverse, accessed on February 28, 2026, https://www.getaiverse.com/post/die-wiederherstellung-historischer-dokumente-mithilfe-von-kuenstlicher-intelligenz
How does AI image generation perform image repair and inpainting?, accessed on February 28, 2026, https://www.tencentcloud.com/techpedia/125175
Generative AI for Planetary Image Reconstruction | by Zaina Haider, accessed on February 28, 2026, https://medium.com/@thekzgroupllc/generative-ai-for-planetary-image-reconstruction-d83028066bba
JPEGHRepairKit: Corrupted JPEG Header Repair Kit using Header, accessed on February 28, 2026, https://publisher.uthm.edu.my/periodicals/index.php/aitcs/article/view/16570
File Repair - AI Repair & Restoration for Photo, Video, and Document, accessed on February 28, 2026, https://www.ireashare.com/file-repair.html
Online File Repair Tool For Corrupted Files, accessed on February 28, 2026, https://online.officerecovery.com/
generative ai for pipeline repair: automating corrective actions in self, accessed on February 28, 2026, https://www.researchgate.net/publication/396161486_GENERATIVE_AI_FOR_PIPELINE_REPAIR_AUTOMATING_CORRECTIVE_ACTIONS_IN_SELF-_HEALING_DATA_SYSTEMS
(PDF) Reconstructing corrupt DEFLATEd files - ResearchGate, accessed on February 28, 2026, https://www.researchgate.net/publication/251703014_Reconstructing_corrupt_DEFLATEd_files
A Study on PSNR and SSIM Metrics with Variable-Sized Hidden, accessed on February 28, 2026, https://www.iieta.org/journals/rces/paper/10.18280/rces.110202
Image Quality Assessment through FSIM, SSIM, MSE and PSNR—A, accessed on February 28, 2026, https://www.scirp.org/journal/paperinformation?paperid=90911
PSNR vs. SSIM: Comparing Image Quality Metrics, accessed on February 28, 2026, https://imageupsize.com/blog/psnr-vs-ssim-comparing-image-quality-metrics
Analysis of Forensic Disk Imaging Tools for Data Acquisition and, accessed on February 28, 2026, https://www.researchgate.net/publication/392843717_Analysis_of_Forensic_Disk_Imaging_Tools_for_Data_Acquisition_and_Preservation
Automated Forensic Recovery Methodology for Video Evidence from, accessed on February 28, 2026, https://www.mdpi.com/2078-2489/16/11/983
Performance Tuning Guide - Intel Open Source Technology Center, accessed on February 28, 2026, https://intel.github.io/intel-extension-for-pytorch/cpu/1.13.0+cpu/tutorials/performance_tuning/tuning_guide.html
API Documentation - Intel Open Source Technology Center, accessed on February 28, 2026, https://intel.github.io/intel-extension-for-pytorch/cpu/latest/tutorials/api_doc.html
Intel® Extension for PyTorch* CPU Jupyter Notebooks - GitHub, accessed on February 28, 2026, https://github.com/intel/intel-extension-for-pytorch/blob/main/examples/cpu/inference/python/jupyter-notebooks/README.md
CPU oneDNN optimization issue - jit - PyTorch Forums, accessed on February 28, 2026, https://discuss.pytorch.org/t/cpu-onednn-optimization-issue/179509
A Survey On Data Carving In Digital Forensics, accessed on February 28, 2026, https://www.forensicfocus.com/articles/a-survey-on-data-carving-in-digital-forensics/
Generative AI for Synthetic Data - Lund University Publications, accessed on February 28, 2026, https://lup.lub.lu.se/student-papers/record/9136467/file/9136469.pdf
a Digital Forensics Dataset for Large Language Models - arXiv.org, accessed on February 28, 2026, https://arxiv.org/html/2509.05331v1
AI-Powered Platform Development Timeline Explained, accessed on February 28, 2026, https://www.abbacustechnologies.com/ai-powered-platform-development-timeline-explained/
AI Development Timeline: How Long Does It Really Take? -, accessed on February 28, 2026, https://techquarter.io/ai-development-timeline-how-long-does-it-take/
Software Development Timeline Guide 2025: Realistic Project, accessed on February 28, 2026, https://appcost.ai/blog/software-development-timeline-guide
How Long Does It Take to Build an AI App: Timelines Explained, accessed on February 28, 2026, https://riseuplabs.com/how-long-does-it-take-to-build-an-ai-app/
(PDF) Assessing the Performance of Forensic File Recovery Tools, accessed on February 28, 2026, https://www.researchgate.net/publication/391862766_Assessing_the_Performance_of_Forensic_File_Recovery_Tools_on_Deleted_Files_from_a_USB_Device
Deep Learning for Digital Forensics: - IGI Global, accessed on February 28, 2026, https://www.igi-global.com/viewtitle.aspx?TitleId=384048&isxn=9798337302454
Automatically generating digital forensic reference data triggered by, accessed on February 28, 2026, https://dfrws.org/wp-content/uploads/2025/10/Automatically-generating-digital-forensic-refe_2025_Forensic-Science-Interna.pdf
