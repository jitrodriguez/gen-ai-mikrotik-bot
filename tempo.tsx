import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  Animated,
  Alert,
} from 'react-native'
import {
  GestureHandlerRootView,
  PanGestureHandler,
} from 'react-native-gesture-handler'
// import Animated, {
//   useSharedValue,
//   withTiming,
//   useAnimatedStyle,
//   Easing,
// } from 'react-native-reanimated';
import { MaterialCommunityIcons } from '@expo/vector-icons'
import { LinearGradient } from 'expo-linear-gradient'
import { Keyframe, useAnimatedStyle, useSharedValue, withSpring } from 'react-native-reanimated';



const GRID_SIZE = 4
const CELL_SIZE = Dimensions.get('window').width * 0.2
const CELL_GAP = 8

interface Cell{
  value: number;
  isNew: boolean;
  isResult: boolean;
}

export default function App() {
  const initialWidth = useSharedValue(CELL_SIZE)
  const [board, setBoard] = useState<Cell[][]>([])
  const [score, setScore] = useState(0)
  const [gameOver, setGameOver] = useState(false)

  // Inicializar el tablero
  useEffect(() => {
    initializeBoard()
  }, [])

  const handlePress = () => {
    initialWidth.value = withSpring(initialWidth.value + 50);
  };
  const getAnimatedStyles = (isResult: boolean) => {
    return useAnimatedStyle(() => {
      const scale = isResult ? withSpring(1.05) : withSpring(1)
      return {
        transform: [{ scale }],
      }
    })
  }
  const initializeBoard = () => {
    const newBoard = Array(GRID_SIZE)
      .fill(0)
      .map(() => Array(GRID_SIZE).fill(0)
        .map(() => ({ value: 0, isNew: false, isResult: false })))
    addRandomTile(addRandomTile(newBoard))
    setBoard(newBoard)
    setScore(0)
    setGameOver(false)
  }

  const addRandomTile = (currentBoard: Cell[][]) => {
    const availableCells = []
    for (let i = 0; i < GRID_SIZE; i++) {
      for (let j = 0; j < GRID_SIZE; j++) {
        if (currentBoard[i][j].value === 0) {
          availableCells.push({ x: i, y: j })
        }
      }
    }

    if (availableCells.length > 0) {
      const randomCell =
        availableCells[Math.floor(Math.random() * availableCells.length)]
      currentBoard[randomCell.x][randomCell.y] = {
        value: Math.random() < 0.9 ? 2 : 4,
        isNew: true,
        isResult: false
      }
    }

    return currentBoard
  }
  const move = (direction: 'left' | 'right' | 'up' | 'down') => {
    let newBoard = JSON.parse(JSON.stringify(board))
    let moved = false
    let newScore = score

    // Reset isNew and isResult flags
    newBoard = newBoard.map(row =>
      row.map(cell => ({ ...cell, isNew: false, isResult: false }))
    )

    const moveLeft = (board: Cell[][]) => {
      for (let i = 0; i < GRID_SIZE; i++) {
        let row = board[i].filter((cell) => cell.value !== 0)
        let j = 0
        while (j < row.length - 1) {
          if (row[j].value === row[j + 1].value) {
            row[j] = {
              value: row[j].value * 2,
              isNew: false,
              isResult: true
            }
            newScore += row[j].value
            row.splice(j + 1, 1)
            moved = true
          }
          j++
        }
        const newRow = row.concat(
          Array(GRID_SIZE - row.length)
            .fill(0)
            .map(() => ({ value: 0, isNew: false, isResult: false }))
        )
        if (JSON.stringify(board[i]) !== JSON.stringify(newRow)) moved = true
        board[i] = newRow
      }
      return board
    }
    const rotateMatrix = (matrix: number[][], times: number = 1) => {
      let newMatrix = JSON.parse(JSON.stringify(matrix))
      for (let t = 0; t < times; t++) {
        const N = newMatrix.length
        const rotated = Array(N)
          .fill(0)
          .map(() => Array(N).fill(0))

        for (let i = 0; i < N; i++) {
          for (let j = 0; j < N; j++) {
            rotated[N - 1 - j][i] = newMatrix[i][j]
          }
        }
        newMatrix = rotated
      }
      return newMatrix
    }
    switch (direction) {
      case 'left':
        newBoard = rotateMatrix(newBoard, 3)
        newBoard = moveLeft(newBoard)
        newBoard = rotateMatrix(newBoard, 1)
        break
      case 'right':
        newBoard = rotateMatrix(newBoard, 1)
        newBoard = moveLeft(newBoard)
        newBoard = rotateMatrix(newBoard, 3)
        break
      case 'up':
        newBoard = moveLeft(newBoard)
        break
      case 'down':
        newBoard = rotateMatrix(newBoard, 2)
        newBoard = moveLeft(newBoard)
        newBoard = rotateMatrix(newBoard, 2)
        break
    }

    if (moved) {
      addRandomTile(newBoard)
      setBoard(newBoard)
      setScore(newScore)

      if (isGameOver(newBoard)) {
        setGameOver(true)
        Alert.alert('Game Over!', `Final Score: ${newScore}`, [
          { text: 'Try Again', onPress: initializeBoard },
        ])
      }
    }
  }

  const rotateBoard = (board: Cell[][], times: number) => {
    for (let i = 0; i < times; i++) {
      const newBoard = Array(GRID_SIZE)
        .fill(0)
        .map(() => Array(GRID_SIZE).fill(0))
      for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
          newBoard[col][GRID_SIZE - 1 - row] = board[row][col]
        }
      }
      for (let row = 0; row < GRID_SIZE; row++) {
        board[row] = [...newBoard[row]]
      }
    }
  }

  const isGameOver = (currentBoard: Cell[][]) => {
    // Verificar si hay movimientos posibles
    for (let i = 0; i < GRID_SIZE; i++) {
      for (let j = 0; j < GRID_SIZE; j++) {
        if (currentBoard[i][j].value === 0) return false
        if (i < GRID_SIZE - 1 && currentBoard[i][j].value === currentBoard[i + 1][j].value)
          return false
        if (j < GRID_SIZE - 1 && currentBoard[i][j].value === currentBoard[i][j + 1].value)
          return false
      }
    }
    return true
  }
  const [isGestureEnabled, setIsGestureEnabled] = useState(true)

  const onGestureEvent = ({ nativeEvent }: any) => {
    if (!isGestureEnabled) return

    const { translationX, translationY } = nativeEvent
    const magnitude = Math.sqrt(
      translationX * translationX + translationY * translationY
    )

    if (magnitude > 30) {
      // Aumentamos el umbral de sensibilidad
      setIsGestureEnabled(false) // Deshabilitamos temporalmente el gesto

      setTimeout(() => {
        setIsGestureEnabled(true) // Rehabilitamos el gesto después de un delay
      }, 250) // Delay de 250ms entre movimientos

      if (Math.abs(translationX) > Math.abs(translationY)) {
        if (translationX > 0) {
          move('left')
        } else {
          move('right')
        }
      } else {
        if (translationY > 0) {
          move('down')
        } else {
          move('up')
        }
      }
    }
  }

  const getCellColor = (cell: Cell) => {
    const colors: { [key: number]: string } = {
      0: '#CDC1B4',
      2: '#EEE4DA',
      4: '#EDE0C8',
      8: '#F2B179',
      16: '#F59563',
      32: '#F67C5F',
      64: '#F65E3B',
      128: '#EDCF72',
      256: '#EDCC61',
      512: '#EDC850',
      1024: '#EDC53F',
      2048: '#EDC22E',
    }
    return colors[cell.value] || '#CDC1B4'
  }

  const getCellTextColor = (value: number) => {
    return value <= 4 ? '#776E65' : '#F9F6F2'
  }

  return (
    <GestureHandlerRootView style={styles.container}>
      <LinearGradient
        colors={['#FAF8EF', '#BBADA0']}
        style={styles.container}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>2048</Text>
            <Text style={styles.subtitle}>
              Join the numbers and get to 2048!
            </Text>
          </View>
          <View style={styles.scoreContainer}>
            <Text style={styles.scoreTitle}>SCORE</Text>
            <Text style={styles.scoreValue}>{score}</Text>
          </View>
        </View>

        <TouchableOpacity
          style={styles.newGameButton}
          onPress={initializeBoard}
        >
          <MaterialCommunityIcons
            name='restart'
            size={24}
            color='#F9F6F2'
          />
          <Text style={styles.newGameText}>New Game</Text>
        </TouchableOpacity>
        <PanGestureHandler onGestureEvent={onGestureEvent}>
          <View style={styles.board}>
            {board.map((row, i) => (
              <View
                key={`row-${i}`}
                style={[
                  styles.row,
                  i === GRID_SIZE - 1 ? { marginBottom: 0 } : null,
                ]}
              >
                {row.map((cell, j) => (
                  <Animated.View
                    key={`${i}-${j}`}
                    style={[
                        styles.cell,
                        {
                          backgroundColor: getCellColor(cell),
                        },
                        getAnimatedStyles(cell.isResult)
                      ]}
                  >
                    {cell.value > 0 && (
                      <Text
                        style={[
                          styles.cellText,
                          {
                            color: getCellTextColor(cell.value),
                            fontSize: cell.value > 100 ? 24 : 32,
                          },
                        ]}
                      >
                        {cell.value}
                      </Text>
                    )}
                  </Animated.View>
                ))}
              </View>
            ))}
          </View>
        </PanGestureHandler>
      </LinearGradient>
    </GestureHandlerRootView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  header: {
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#776E65',
  },
  subtitle: {
    color: '#776E65',
    fontSize: 16,
  },
  scoreContainer: {
    backgroundColor: '#BBADA0',
    padding: 10,
    borderRadius: 6,
    alignItems: 'center',
    minWidth: 100,
  },
  scoreTitle: {
    color: '#EEE4DA',
    fontSize: 13,
    fontWeight: 'bold',
  },
  scoreValue: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: 'bold',
  },
  newGameButton: {
    backgroundColor: '#8F7A66',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
    marginBottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  newGameText: {
    color: '#F9F6F2',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  board: {
    backgroundColor: '#BBADA0',
    padding: CELL_GAP,
    borderRadius: 6,
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: CELL_SIZE * 4 + CELL_GAP * 5,
    height: CELL_SIZE * 4 + CELL_GAP * 5,
    justifyContent: 'space-between',
  },
  cell: {
    // width: CELL_SIZE,
    height: CELL_SIZE,
    backgroundColor: '#CDC1B4',
    borderRadius: 3,
    alignItems: 'center',
    justifyContent: 'center',
    margin: 0,
    marginBottom: 8,
  },
  cellText: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  row: {},
})
