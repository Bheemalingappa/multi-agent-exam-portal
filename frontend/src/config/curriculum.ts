export interface SubjectConfig {
  title: string;
  query: string;
  category: string;
  description: string;
}

export interface ClassCurriculum {
  level: number;
  name: string;
  category: 'primary' | 'middle' | 'high' | 'higher';
  description: string;
  subjects: SubjectConfig[];
}

export const CLASS_CURRICULUM: Record<number, ClassCurriculum> = {
  1: {
    level: 1,
    name: 'Class 1',
    category: 'primary',
    description: 'Foundational Numbers, Alphabet & Environmental Awareness',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'Numbers', description: 'Addition, Subtraction, Counting & Shapes' },
      { title: 'English', query: 'english', category: 'Language', description: 'Phonetics, Vocabulary & Simple Sentences' },
      { title: 'Environmental Studies', query: 'science', category: 'General', description: 'Plants, Animals, Family & Neighborhood' },
    ],
  },
  2: {
    level: 2,
    name: 'Class 2',
    category: 'primary',
    description: 'Basic Math, Reading Skills & Nature Science',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'Numbers', description: '2-Digit Addition, Subtraction & Measurement' },
      { title: 'English', query: 'english', category: 'Language', description: 'Grammar, Story Reading & Writing' },
      { title: 'Environmental Studies', query: 'science', category: 'General', description: 'Our Body, Food, Water & Seasons' },
    ],
  },
  3: {
    level: 3,
    name: 'Class 3',
    category: 'primary',
    description: 'Introductory Multiplication, Science & Social Science',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'Arithmetic', description: 'Multiplication, Division & Fractions Intro' },
      { title: 'Science', query: 'science', category: 'Natural Science', description: 'Living Things, Matter & Environment' },
      { title: 'English', query: 'english', category: 'Language', description: 'Comprehension, Nouns & Verbs' },
      { title: 'Social Studies', query: 'social', category: 'Humanities', description: 'Maps, Local Governance & History Stories' },
    ],
  },
  4: {
    level: 4,
    name: 'Class 4',
    category: 'primary',
    description: 'Fractions, Decimals, Environmental Science & Computers',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'Arithmetic', description: 'Long Division, Decimals & Perimeter' },
      { title: 'Science', query: 'science', category: 'Natural Science', description: 'Plant Physiology, Digestive System & Energy' },
      { title: 'English', query: 'english', category: 'Language', description: 'Grammar Rules, Paragraphs & Poetry' },
      { title: 'Social Studies', query: 'social', category: 'Humanities', description: 'Landforms of India, Heritage & Civics' },
    ],
  },
  5: {
    level: 5,
    name: 'Class 5',
    category: 'primary',
    description: 'Primary Board Prep, Mathematics & Natural Science',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'Arithmetic', description: 'Large Numbers, Factors, Multiples & Geometry' },
      { title: 'Science', query: 'science', category: 'Natural Science', description: 'Human Body Systems, Force, Work & Energy' },
      { title: 'English', query: 'english', category: 'Language', description: 'Formal Letters, Reading Comprehension & Tenses' },
      { title: 'Social Studies', query: 'social', category: 'Humanities', description: 'Globe & Maps, Climate Zones & Freedom Movement' },
    ],
  },
  6: {
    level: 6,
    name: 'Class 6',
    category: 'middle',
    description: 'Integers, Physics Fundamentals & Earth Studies',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'STEM', description: 'Integers, Algebra Intro, Ratio & Symmetry' },
      { title: 'Science', query: 'science', category: 'STEM', description: 'Components of Food, Light, Electricity & Magnetism' },
      { title: 'English', query: 'english', category: 'Language', description: 'Literature, Grammar & Essay Writing' },
      { title: 'Social Studies', query: 'social', category: 'Humanities', description: 'Ancient History, Earth in Solar System & Panchayati Raj' },
      { title: 'Computer Science', query: 'python', category: 'Technology', description: 'Computer Basics, Logic & Intro to Coding' },
    ],
  },
  7: {
    level: 7,
    name: 'Class 7',
    category: 'middle',
    description: 'Algebraic Expressions, Chemistry & Medieval History',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'STEM', description: 'Fractions, Decimals, Algebraic Expressions & Triangles' },
      { title: 'Science', query: 'science', category: 'STEM', description: 'Nutrition, Heat, Acids, Bases & Motion' },
      { title: 'English', query: 'english', category: 'Language', description: 'Prose, Poetry, Active/Passive Voice' },
      { title: 'Social Studies', query: 'social', category: 'Humanities', description: 'Medieval India, Environment & State Government' },
      { title: 'Computer Science', query: 'python', category: 'Technology', description: 'Control Flow, Variables & Python Basics' },
    ],
  },
  8: {
    level: 8,
    name: 'Class 8',
    category: 'middle',
    description: 'Linear Equations, Force & Pressure, Computer Logic',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'STEM', description: 'Rational Numbers, Linear Equations, Mensuration & Graphs' },
      { title: 'Science', query: 'science', category: 'STEM', description: 'Force & Pressure, Friction, Sound & Microorganisms' },
      { title: 'English', query: 'english', category: 'Language', description: 'Reported Speech, Articles & Analytical Writing' },
      { title: 'Social Studies', query: 'social', category: 'Humanities', description: 'Modern India, Resources, Judiciary & Secularism' },
      { title: 'Computer Science', query: 'python', category: 'Technology', description: 'Functions, Data Structures & Python Algorithms' },
    ],
  },
  9: {
    level: 9,
    name: 'Class 9',
    category: 'high',
    description: 'Polynomials, Motion, Atoms & World History',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'High School', description: 'Polynomials, Coordinate Geometry, Triangles & Statistics' },
      { title: 'Science', query: 'science', category: 'High School', description: 'Motion, Gravitation, Atoms, Molecules & Cell Structure' },
      { title: 'English', query: 'english', category: 'Language', description: 'Literature Companion, Formal Essays & Editing' },
      { title: 'Social Science', query: 'social', category: 'Humanities', description: 'French Revolution, Socialism, Climate & Electoral Politics' },
      { title: 'Computer Science', query: 'python', category: 'Technology', description: 'Python OOP, Lists, Dictionaries & Algorithm Design' },
    ],
  },
  10: {
    level: 10,
    name: 'Class 10',
    category: 'high',
    description: 'Quadratic Equations, Light, Trigonometry & Board Exams',
    subjects: [
      { title: 'Mathematics', query: 'quadratic', category: 'High School', description: 'Quadratic Equations, Trigonometry, Circles & Probability' },
      { title: 'Science', query: 'science', category: 'High School', description: 'Chemical Reactions, Light Reflection, Electricity & Heredity' },
      { title: 'English', query: 'english', category: 'Language', description: 'Board Literature, Analytical Paragraphs & Grammar' },
      { title: 'Social Science', query: 'social', category: 'Humanities', description: 'Nationalism in India, Agriculture, Power Sharing & Economy' },
      { title: 'Computer Science', query: 'python', category: 'Technology', description: 'Data Structures, Recursion, File I/O & Algorithmic Logic' },
    ],
  },
  11: {
    level: 11,
    name: 'Class 11',
    category: 'higher',
    description: 'Calculus, Electromagnetism, Organic Chemistry & CS',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'Higher Secondary', description: 'Sets, Trigonometric Functions, Calculus & Probability' },
      { title: 'Physics', query: 'physics', category: 'Higher Secondary', description: 'Kinematics, Laws of Motion, Thermodynamics & Oscillations' },
      { title: 'Chemistry', query: 'chemistry', category: 'Higher Secondary', description: 'Atomic Structure, Chemical Bonding & Hydrocarbons' },
      { title: 'Biology', query: 'biology', category: 'Higher Secondary', description: 'Cell Division, Plant Physiology & Human Physiology' },
      { title: 'English', query: 'english', category: 'Language', description: 'Advanced Reading, Creative Writing & Literature' },
      { title: 'Computer Science', query: 'python', category: 'Technology', description: 'Python Modules, Stack Data Structure & SQL Basics' },
    ],
  },
  12: {
    level: 12,
    name: 'Class 12',
    category: 'higher',
    description: 'Higher Mathematics, Quantum Physics & AI Assessment',
    subjects: [
      { title: 'Mathematics', query: 'math', category: 'Higher Secondary', description: 'Matrices, Integration, Differential Equations & Vectors' },
      { title: 'Physics', query: 'physics', category: 'Higher Secondary', description: 'Electrostatics, Optics, Quantum Physics & Semiconductors' },
      { title: 'Chemistry', query: 'chemistry', category: 'Higher Secondary', description: 'Electrochemistry, Organic Reactions & Biomolecules' },
      { title: 'Biology', query: 'biology', category: 'Higher Secondary', description: 'Genetics, Biotechnology, Evolution & Ecology' },
      { title: 'English', query: 'english', category: 'Language', description: 'Advanced Literature & Discourse Analysis' },
      { title: 'Computer Science', query: 'python', category: 'Technology', description: 'Complex Data Structures, Networking & AI Evaluation' },
    ],
  },
};
